"""Assemble final 9:16 Short MP4 from production pack (ffmpeg)."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RenderedVideo:
    draft_id: int
    output_path: Path
    duration_seconds: float
    message: str


def _probe_duration(audio_path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        text=True,
    )
    return float(out.strip())


def _scaled_durations(segments: list[dict], audio_duration: float) -> list[float]:
    manifest_total = segments[-1]["end_seconds"]
    if manifest_total <= 0:
        raise ValueError("Invalid segment timing in manifest.")
    scale = audio_duration / manifest_total
    durs: list[float] = []
    for seg in segments:
        raw = seg["end_seconds"] - seg["start_seconds"]
        durs.append(max(0.35, raw * scale))
    # Normalize so sum matches audio exactly
    total = sum(durs)
    if total > 0:
        fix = audio_duration / total
        durs = [d * fix for d in durs]
    return durs


def _write_concat(images_dir: Path, segments: list[dict], durations: list[float], concat_path: Path) -> None:
    lines = ["ffconcat version 1.0"]
    for seg, dur in zip(segments, durations):
        img = images_dir / seg["filename"]
        if not img.exists():
            raise FileNotFoundError(f"Missing image: {img}")
        lines.append(f"file '{img.resolve()}'")
        lines.append(f"duration {dur:.4f}")
    last = (images_dir / segments[-1]["filename"]).resolve()
    lines.append(f"file '{last}'")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_short_video(
    pack_dir: Path,
    *,
    draft_id: int,
    audio_name: str = "voiceover.mp3",
    output_name: str = "final_short.mp4",
) -> RenderedVideo:
    """Build H.264 Short from manifest segments + voiceover audio."""
    manifest_path = pack_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest at {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    segments = manifest.get("segments") or []
    if not segments:
        raise ValueError("Manifest has no segments.")

    audio_path = pack_dir / audio_name
    if not audio_path.exists():
        raise FileNotFoundError(f"No audio at {audio_path}")

    images_dir = pack_dir / "images"
    audio_duration = _probe_duration(audio_path)
    durations = _scaled_durations(segments, audio_duration)

    concat_path = pack_dir / "_concat.txt"
    out_path = pack_dir / output_name
    _write_concat(images_dir, segments, durations, concat_path)

    from shorts_bot.config import settings
    from shorts_bot.production.captions import burn_captions_via_ffmpeg
    from shorts_bot.production.subtitles import ffmpeg_subtitles_filter, write_subtitle_files

    ass_path = write_subtitle_files(pack_dir, segments, audio_duration)

    vf = "format=yuv420p"
    if burn_captions_via_ffmpeg() or settings.burn_in_subtitles:
        vf = ffmpeg_subtitles_filter(ass_path)

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_path),
        "-i",
        str(audio_path),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        "-t",
        f"{audio_duration:.3f}",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)

    return RenderedVideo(
        draft_id=draft_id,
        output_path=out_path,
        duration_seconds=audio_duration,
        message=(
            f"Rendered {out_path.name} ({audio_duration:.1f}s, 1080×1920). "
            f"Captions: ffmpeg ASS burn-in + captions.srt for YouTube."
        ),
    )
