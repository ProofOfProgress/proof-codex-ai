"""Ambient + SFX bed for launch-phase Shorts — no Kling speech, full horror sound design."""

from __future__ import annotations

import subprocess
from pathlib import Path


def create_launch_ambient_bed(
    duration: float,
    dest: Path,
    *,
    bitrate_k: int = 192,
) -> Path:
    """Wind + low drone when Kling clips are silent (blocks speech, keeps atmosphere)."""
    dur = max(1.0, float(duration))
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"anoisesrc=color=pink:duration={dur:.3f}:sample_rate=48000,"
            "lowpass=f=450,highpass=f=60,volume=0.16",
            "-f",
            "lavfi",
            "-i",
            f"aevalsrc='0.07*sin(2*PI*42*t)':d={dur:.3f}:sample_rate=48000",
            "-filter_complex",
            "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=0[out]",
            "-map",
            "[out]",
            "-c:a",
            "libmp3lame",
            "-b:a",
            f"{bitrate_k}k",
            str(dest),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return dest


def extract_or_build_kling_audio(
    merged_video: Path,
    dest: Path,
    *,
    draft_id: int | None,
    duration: float,
    bitrate_k: int = 192,
) -> Path:
    """Launch phase → ambient bed + post SFX. Later drafts → Kling native audio."""
    from shorts_bot.production.launch_phase import is_silent_launch_draft

    if is_silent_launch_draft(draft_id):
        return create_launch_ambient_bed(duration, dest, bitrate_k=bitrate_k)

    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "csv=p=0",
            str(merged_video),
        ],
        capture_output=True,
        text=True,
    )
    if "audio" not in (probe.stdout or ""):
        return create_launch_ambient_bed(duration, dest, bitrate_k=bitrate_k)

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(merged_video),
            "-vn",
            "-acodec",
            "libmp3lame",
            "-b:a",
            f"{bitrate_k}k",
            str(dest),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return dest
