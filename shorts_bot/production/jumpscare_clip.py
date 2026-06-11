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
    """Return (setup_seconds, scare_play_seconds) for finale segment."""
    play = min(
        max(1.2, settings.jumpscare_clip_play_seconds),
        segment_duration * 0.55,
    )
    play = min(play, segment_duration - settings.jumpscare_setup_min_seconds)
    play = max(1.0, play)
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
    vf = f"scale={width}:{height}:flags=lanczos,format=yuv420p"
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
    from shorts_bot.production.render_ai_video import render_ai_video_clip
    from shorts_bot.production.segment_sync import resolve_segments, normalize_transcript_segments
    from shorts_bot.production.render_video import _probe_duration
    from shorts_bot.memory.store import MemoryStore

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

    if (
        not force
        and out.exists()
        and out.stat().st_size > 10_000
        and stem_clip.exists()
        and stem_clip.stat().st_size > 10_000
    ):
        return out

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
    image_path = images_dir / f"{brief.filename_stem}.png"
    if not image_path.exists():
        from shorts_bot.production.images.router import generate_image

        generate_image(brief.prompt, image_path)

    ok = render_ai_video_clip(
        brief,
        seg,
        topic=topic,
        clip_index=idx,
        image_path=image_path,
        clip_path=stem_clip,
        pack_dir=pack_dir,
    )
    if not ok or not stem_clip.exists():
        err = stem_clip.with_suffix(".error.txt")
        detail = err.read_text(encoding="utf-8") if err.exists() else "I2V failed"
        raise RuntimeError(f"Jumpscare I2V failed: {detail}")

    shutil.copy2(stem_clip, out)
    return out
