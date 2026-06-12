"""Dedicated jumpscare I2V clip — short Hailuo lunge, not slideshow zoompan."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from shorts_bot.config import settings

JUMPSCARE_CLIP_FILENAME = "jumpscare_lunge.mp4"


def jumpscare_clip_path(clips_dir: Path) -> Path:
    return clips_dir / JUMPSCARE_CLIP_FILENAME


def probe_clip_duration(video_path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        text=True,
    )
    return float(out.strip())


def scare_play_and_setup_durations(segment_duration: float) -> tuple[float, float]:
    """Return (setup_seconds, scare_play_seconds) — scare video gets the majority."""
    play = min(
        max(1.5, settings.jumpscare_clip_play_seconds),
        segment_duration * 0.72,
    )
    play = min(play, segment_duration - settings.jumpscare_setup_min_seconds)
    play = max(1.2, play)
    setup = max(settings.jumpscare_setup_min_seconds, segment_duration - play)
    return setup, play


def trim_jumpscare_impact(
    src: Path,
    dest: Path,
    *,
    play_seconds: float,
    width: int,
    height: int,
) -> None:
    """
    Take the tail of a Hailuo lunge clip and play at native speed (no zoompan slideshow).
    """
    src_dur = probe_clip_duration(src)
    tail = min(max(1.0, settings.jumpscare_i2v_tail_seconds), src_dur)
    start = max(0.0, src_dur - tail)
    play = min(play_seconds, tail)
    from shorts_bot.production.render_video import _jumpscare_video_filter

    scare_vf = _jumpscare_video_filter(play, width=width, height=height)
    vf = f"scale={width}:{height}:flags=lanczos,format=yuv420p,{scare_vf}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{start:.3f}",
            "-i",
            str(src.resolve()),
            "-t",
            f"{play:.4f}",
            "-vf",
            vf,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
            str(dest),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def trim_setup_hold(
    *,
    still_path: Path | None,
    clip_path: Path | None,
    dest: Path,
    duration: float,
    width: int,
    height: int,
) -> None:
    """Hold or trim a setup beat before the lunge (figure at bed / pre-scare)."""
    vf = f"scale={width}:{height}:flags=lanczos,format=yuv420p"
    dest.parent.mkdir(parents=True, exist_ok=True)

    if clip_path and clip_path.exists() and clip_path.stat().st_size > 5000:
        src_dur = probe_clip_duration(clip_path)
        start = max(0.0, src_dur - duration)
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                f"{start:.3f}",
                "-i",
                str(clip_path.resolve()),
                "-t",
                f"{duration:.4f}",
                "-vf",
                vf,
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-pix_fmt",
                "yuv420p",
                str(dest),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return

    if still_path and still_path.exists():
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-i",
                str(still_path.resolve()),
                "-t",
                f"{duration:.4f}",
                "-vf",
                vf,
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-pix_fmt",
                "yuv420p",
                str(dest),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return

    raise FileNotFoundError("Jumpscare setup needs a prior clip or still")


def concat_clips(parts: list[Path], dest: Path) -> None:
    concat_path = dest.parent / "_jumpscare_concat.txt"
    lines = ["ffconcat version 1.0"]
    for part in parts:
        lines.append(f"file '{part.resolve()}'")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-c",
            "copy",
            str(dest),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def compose_finale_jumpscare_segment(
    *,
    jumpscare_src: Path,
    dest: Path,
    segment_duration: float,
    setup_still: Path | None,
    setup_clip: Path | None,
    width: int,
    height: int,
) -> Path:
    """
    Finale = short setup hold + dedicated Hailuo lunge tail (real motion, not Ken Burns).
    """
    tmp = dest.parent
    setup_dur, scare_play = scare_play_and_setup_durations(segment_duration)
    setup_part = tmp / f"{dest.stem}_setup.mp4"
    scare_part = tmp / f"{dest.stem}_scare.mp4"

    trim_setup_hold(
        still_path=setup_still,
        clip_path=setup_clip,
        dest=setup_part,
        duration=setup_dur,
        width=width,
        height=height,
    )
    trim_jumpscare_impact(
        jumpscare_src,
        scare_part,
        play_seconds=scare_play,
        width=width,
        height=height,
    )
    concat_clips([setup_part, scare_part], dest)
    return dest


def jumpscare_clip_meta_path(pack_dir: Path) -> Path:
    return pack_dir / "jumpscare_clip.json"


def load_jumpscare_clip_meta(pack_dir: Path) -> dict | None:
    path = jumpscare_clip_meta_path(pack_dir)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_jumpscare_clip_meta(pack_dir: Path, *, stem: str, model: str, template_id: str) -> None:
    jumpscare_clip_meta_path(pack_dir).write_text(
        json.dumps(
            {
                "source_stem": stem,
                "template_id": template_id,
                "clip_file": JUMPSCARE_CLIP_FILENAME,
                "model": model,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def jumpscare_clip_is_valid(pack_dir: Path, clips_dir: Path) -> bool:
    """True when a dedicated Hailuo lunge file exists and was tagged as such."""
    clip = jumpscare_clip_path(clips_dir)
    if not clip.exists() or clip.stat().st_size < 10_000:
        return False
    meta = load_jumpscare_clip_meta(pack_dir)
    if not meta:
        return False
    model = str(meta.get("model") or "").lower()
    return "hailuo" in model


def _load_jumpscare_segment_index(manifest: dict) -> int | None:
    plan = manifest.get("jumpscare_plan") or {}
    if not plan.get("has_jumpscare", True):
        return None
    segments = manifest.get("segments") or []
    if not segments:
        return None
    idx = int(plan.get("primary_segment_index", len(segments) - 1))
    return min(max(0, idx), len(segments) - 1)


def render_dedicated_jumpscare_clip(
    pack_dir: Path,
    *,
    force: bool = False,
) -> Path:
    """
    Regenerate ONLY the finale Hailuo I2V lunge clip.

    Writes clips/jumpscare_lunge.mp4 and mirrors to the segment stem clip.
    """
    from shorts_bot.production.image_prompts import build_image_briefs
    from shorts_bot.production.render_ai_video import (
        _video_prompt_for_segment,
        replicate_i2v_model_for_clip,
    )
    from shorts_bot.production.segment_sync import resolve_segments, normalize_transcript_segments
    from shorts_bot.production.render_video import _probe_duration
    from shorts_bot.memory.store import MemoryStore

    if not settings.has_paid_images or not (settings.replicate_api_token or "").strip():
        raise RuntimeError(
            "Jumpscare requires Replicate I2V (REPLICATE_API_TOKEN). "
            "Cannot use still-image slideshow for the scare beat."
        )

    manifest_path = pack_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest at {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    idx = _load_jumpscare_segment_index(manifest)
    if idx is None:
        raise RuntimeError("Draft has no finale jumpscare plan")

    draft_id = int(manifest.get("draft_id", 0))
    topic = str(manifest.get("topic") or "")
    clips_dir = pack_dir / "clips"
    images_dir = pack_dir / "images"
    clips_dir.mkdir(parents=True, exist_ok=True)

    out = jumpscare_clip_path(clips_dir)
    seg_row = manifest["segments"][idx]
    stem = Path(seg_row["filename"]).stem
    stem_clip = clips_dir / f"{stem}.mp4"

    if not force and jumpscare_clip_is_valid(pack_dir, clips_dir):
        return out

    for path in (out, stem_clip, stem_clip.with_suffix(".error.txt")):
        if path.exists():
            path.unlink()

    store = MemoryStore(settings.database_path)
    draft = store.get_draft(draft_id)
    audio_path = pack_dir / "voiceover.mp3"
    audio_duration = _probe_duration(audio_path) if audio_path.exists() else None
    segments, _ = resolve_segments(
        script=draft.script,
        pack_dir=pack_dir,
        audio_duration=audio_duration,
    )
    if audio_duration:
        segments = normalize_transcript_segments(segments, audio_duration)

    beats = manifest.get("visual_beats") or []
    briefs = build_image_briefs(segments, topic=topic, visual_beats=beats)
    if idx >= len(briefs) or idx >= len(segments):
        raise RuntimeError(f"Jumpscare segment index {idx} out of range")

    brief = briefs[idx]
    seg = segments[idx]
    # Manifest stems (e.g. 00.28) are authoritative — brief stems can drift after resync.
    image_name = str(seg_row.get("filename") or f"{stem}.png")
    image_path = images_dir / image_name
    if not image_path.exists():
        from shorts_bot.production.images.router import generate_image

        generate_image(brief.prompt, image_path)

    motion_prompt, model_hint, template_id = _video_prompt_for_segment(
        seg,
        topic=topic,
        clip_index=idx,
        pack_dir=pack_dir,
        filename_stem=stem,
    )
    if not motion_prompt:
        from shorts_bot.production.ai_video_prompts import match_template, segment_to_video_prompt

        tmpl = match_template(topic=topic, spoken_text=seg.text, segment_index=idx)
        if tmpl.id != "jumpscare_lunge":
            from shorts_bot.production.ai_video_prompts import templates

            tmpl = next(t for t in templates() if t.id == "jumpscare_lunge")
        motion_prompt = segment_to_video_prompt(seg, topic=topic, template=tmpl, clip_index=idx)
        template_id = tmpl.id
        model_hint = tmpl.model_hint

    model = replicate_i2v_model_for_clip(
        model_hint=model_hint or "hailuo",
        template_id=template_id or "jumpscare_lunge",
    )
    from shorts_bot.production.images.replicate import generate_replicate_i2v

    try:
        generate_replicate_i2v(
            motion_prompt,
            image_path,
            stem_clip,
            token=(settings.replicate_api_token or "").strip(),
            model=model,
            timeout_sec=settings.ai_video_timeout_sec,
        )
    except Exception as exc:
        stem_clip.with_suffix(".error.txt").write_text(str(exc), encoding="utf-8")
        raise RuntimeError(f"Jumpscare I2V failed: {exc}") from exc

    if not stem_clip.exists():
        raise RuntimeError("Jumpscare I2V failed: no output clip")
    if "hailuo" not in model.lower():
        raise RuntimeError(f"Jumpscare must use Hailuo I2V, got {model}")

    shutil.copy2(stem_clip, out)
    save_jumpscare_clip_meta(
        pack_dir,
        stem=stem,
        model=model,
        template_id=template_id or "jumpscare_lunge",
    )
    return out


def ensure_jumpscare_video_clip(pack_dir: Path, *, force: bool = False) -> Path:
    """
    Guarantee clips/jumpscare_lunge.mp4 exists (Hailuo I2V) before final render.

    Raises if the scare cannot be a real motion clip.
    """
    clips_dir = pack_dir / "clips"
    if not force and jumpscare_clip_is_valid(pack_dir, clips_dir):
        return jumpscare_clip_path(clips_dir)
    from shorts_bot.production.ai_video_guard import require_ai_video_generation

    require_ai_video_generation(action="jumpscare I2V")
    return render_dedicated_jumpscare_clip(pack_dir, force=True)
