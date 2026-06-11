"""Paid AI video clips — FLUX still → Replicate I2V per beat (full motion, not slideshow)."""

from __future__ import annotations

import time
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.ai_video_prompts import build_video_prompt_briefs, match_template, segment_to_video_prompt
from shorts_bot.production.image_prompts import ImageBrief
from shorts_bot.production.images.replicate import generate_replicate_i2v
from shorts_bot.production.images.router import generate_image
from shorts_bot.production.turboscribe_parser import TranscriptSegment


def select_i2v_beat_indices(segment_count: int, max_beats: int) -> list[int]:
    """Always render hook (0) + finale; evenly sample middle when capped."""
    if segment_count <= 0:
        return []
    if max_beats >= segment_count:
        return list(range(segment_count))
    if max_beats <= 1:
        return [0]
    selected = {0, segment_count - 1}
    remaining = max_beats - len(selected)
    middle = list(range(1, segment_count - 1))
    if remaining <= 0 or not middle:
        return sorted(selected)[:max_beats]
    if remaining >= len(middle):
        selected.update(middle)
        return sorted(selected)
    step = len(middle) / remaining
    for i in range(remaining):
        selected.add(middle[int(i * step)])
    return sorted(selected)


def _video_prompt_for_segment(seg: TranscriptSegment, *, topic: str, clip_index: int) -> str:
    tmpl = match_template(topic=topic, spoken_text=seg.text)
    return segment_to_video_prompt(seg, topic=topic, template=tmpl, clip_index=clip_index)


def render_ai_video_clip(
    image_brief: ImageBrief,
    seg: TranscriptSegment,
    *,
    topic: str,
    clip_index: int,
    image_path: Path,
    clip_path: Path,
) -> bool:
    """One beat: generate still (if needed) → I2V motion clip."""
    try:
        if not image_path.exists():
            generate_image(image_brief.prompt, image_path)

        motion_prompt = _video_prompt_for_segment(seg, topic=topic, clip_index=clip_index)
        token = (settings.replicate_api_token or "").strip()
        model = (settings.replicate_video_model or "minimax/video-01").strip()
        generate_replicate_i2v(
            motion_prompt,
            image_path,
            clip_path,
            token=token,
            model=model,
            timeout_sec=settings.ai_video_timeout_sec,
        )
        return True
    except Exception as exc:
        err_path = clip_path.with_suffix(".error.txt")
        err_path.write_text(str(exc), encoding="utf-8")
        return False


def render_all_ai_video_clips(
    briefs: list[ImageBrief],
    segments: list[TranscriptSegment],
    *,
    topic: str,
    images_dir: Path,
    clips_dir: Path,
) -> int:
    """Generate one I2V MP4 per segment; pace Replicate to avoid 429s."""
    clips_dir.mkdir(parents=True, exist_ok=True)
    pace = max(0.0, float(settings.ai_video_pace_sec))
    max_beats = max(1, int(settings.ai_video_max_beats))
    count = 0

    indices = select_i2v_beat_indices(len(segments), max_beats)
    for render_i, seg_i in enumerate(indices):
        if seg_i >= len(briefs) or seg_i >= len(segments):
            continue
        brief, seg = briefs[seg_i], segments[seg_i]
        if pace and render_i > 0:
            time.sleep(pace)
        image_path = images_dir / f"{brief.filename_stem}.png"
        clip_path = clips_dir / f"{brief.filename_stem}.mp4"
        if clip_path.exists() and clip_path.stat().st_size > 10_000:
            count += 1
            continue
        if render_ai_video_clip(
            brief,
            seg,
            topic=topic,
            clip_index=seg_i,
            image_path=image_path,
            clip_path=clip_path,
        ):
            count += 1

    return count
