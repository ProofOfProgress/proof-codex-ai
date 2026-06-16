"""Paid AI video clips — FLUX still → Replicate I2V per beat (full motion, not slideshow)."""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.ai_video_prompts import build_video_prompt_briefs, match_template, segment_to_video_prompt
from shorts_bot.production.image_prompts import ImageBrief
from shorts_bot.production.images.replicate import generate_replicate_i2v
from shorts_bot.production.images.router import generate_image
from shorts_bot.production.turboscribe_parser import TranscriptSegment


def select_i2v_beat_indices(
    segment_count: int,
    max_beats: int,
    *,
    priority_indices: list[int] | None = None,
) -> list[int]:
    """Always render hook (0) + finale; sample middle when capped."""
    if segment_count <= 0:
        return []
    if max_beats >= segment_count:
        return list(range(segment_count))
    if max_beats <= 1:
        return [0]
    selected = {0, segment_count - 1}
    for idx in priority_indices or []:
        if 0 <= idx < segment_count:
            selected.add(idx)
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


def replicate_i2v_model_for_clip(
    *,
    model_hint: str = "",
    template_id: str = "",
) -> str:
    """Role-based Replicate routing inside the existing I2V stack."""
    hint = (model_hint or "").strip().lower()
    tmpl = (template_id or "").strip().lower()
    if tmpl in {"jumpscare_lunge", "jumpscare_tease"} or hint == "hailuo":
        return (settings.replicate_video_model_jumpscare or "minimax/hailuo-2.3-fast").strip()
    if tmpl.endswith("_motion") or hint in {"veo", "runway"}:
        return (settings.replicate_video_model_hook or settings.replicate_video_model).strip()
    return (settings.replicate_video_model or "minimax/video-01").strip()


def _load_video_prompt_pack(pack_dir: Path) -> dict:
    path = pack_dir / "video_prompts.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _clip_spec_from_pack(pack_dir: Path, filename_stem: str) -> tuple[str, str, str]:
    """Return (motion_prompt, model_hint, template_id) from exported video_prompts pack."""
    payload = _load_video_prompt_pack(pack_dir)
    for clip in payload.get("clips") or []:
        if str(clip.get("filename_stem")) == filename_stem:
            prompt_file = clip.get("prompt_file")
            prompt = ""
            if prompt_file:
                path = pack_dir / str(prompt_file)
                if path.exists():
                    prompt = path.read_text(encoding="utf-8").strip()
            if not prompt:
                prompt = str(clip.get("prompt") or "").strip()
            return (
                prompt,
                str(clip.get("model_hint") or ""),
                str(clip.get("template_id") or ""),
            )
    return "", "", ""


def _video_prompt_for_segment(
    seg: TranscriptSegment,
    *,
    topic: str,
    clip_index: int,
    pack_dir: Path | None = None,
    filename_stem: str = "",
) -> tuple[str, str, str]:
    """Prefer exported video_prompts/*.txt; fall back to live template match."""
    if pack_dir and filename_stem:
        prompt, hint, tmpl_id = _clip_spec_from_pack(pack_dir, filename_stem)
        if prompt:
            return prompt, hint, tmpl_id

    tmpl = match_template(topic=topic, spoken_text=seg.text, segment_index=clip_index)
    return (
        segment_to_video_prompt(seg, topic=topic, template=tmpl, clip_index=clip_index),
        tmpl.model_hint,
        tmpl.id,
    )


def render_ai_video_clip(
    image_brief: ImageBrief,
    seg: TranscriptSegment,
    *,
    topic: str,
    clip_index: int,
    image_path: Path,
    clip_path: Path,
    pack_dir: Path | None = None,
) -> bool:
    """One beat: generate still (if needed) → I2V motion clip."""
    from shorts_bot.production.ai_video_guard import require_ai_video_generation

    require_ai_video_generation(action="render_ai_video_clip")
    try:
        if not image_path.exists():
            generate_image(image_brief.prompt, image_path, style_id=image_brief.recraft_style_id)

        motion_prompt, model_hint, template_id = _video_prompt_for_segment(
            seg,
            topic=topic,
            clip_index=clip_index,
            pack_dir=pack_dir,
            filename_stem=image_brief.filename_stem,
        )
        token = (settings.replicate_api_token or "").strip()
        model = replicate_i2v_model_for_clip(model_hint=model_hint, template_id=template_id)
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
    priority_indices: list[int] | None = None,
) -> int:
    """Generate one I2V MP4 per segment; pace Replicate to avoid 429s."""
    clips_dir.mkdir(parents=True, exist_ok=True)
    pack_dir = clips_dir.parent
    pace = max(0.0, float(settings.ai_video_pace_sec))
    from shorts_bot.production.content_format import effective_max_i2v_beats

    max_beats = effective_max_i2v_beats()
    if max_beats <= 0:
        return 0
    count = 0

    indices = select_i2v_beat_indices(len(segments), max_beats, priority_indices=priority_indices)
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
            pack_dir=pack_dir,
        ):
            count += 1
            _, _, template_id = _video_prompt_for_segment(
                seg,
                topic=topic,
                clip_index=seg_i,
                pack_dir=pack_dir,
                filename_stem=brief.filename_stem,
            )
            if template_id in {"jumpscare_lunge", "jumpscare_tease"}:
                from shorts_bot.production.jumpscare_clip import (
                    jumpscare_clip_path,
                    save_jumpscare_clip_meta,
                )

                model = replicate_i2v_model_for_clip(template_id=template_id)
                shutil.copy2(clip_path, jumpscare_clip_path(clips_dir))
                save_jumpscare_clip_meta(
                    pack_dir,
                    stem=brief.filename_stem,
                    model=model,
                    template_id=template_id,
                )

    return count
