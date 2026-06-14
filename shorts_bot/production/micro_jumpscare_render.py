"""Assemble 3s micro-jumpscare Short — single Blender lunge + volume sting, no VO."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.horror_sfx_mix import SfxCue, mix_horror_sfx_into_voiceover


@dataclass
class MicroJumpscareResult:
    output_path: Path
    duration_seconds: float
    sting_at: float
    message: str


def _probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path),
        ],
        text=True,
    ).strip()
    return max(0.1, float(out))


def _create_near_silent_bed(duration: float, dest: Path) -> Path:
    """Whisper wind only — contrast for the sting."""
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
            "lowpass=f=320,highpass=f=40,volume=0.04",
            "-c:a",
            "libmp3lame",
            "-b:a",
            f"{settings.video_audio_bitrate_k}k",
            str(dest),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return dest


def render_micro_jumpscare_final(
    pack_dir: Path,
    *,
    draft_id: int,
    clip_path: Path | None = None,
    output_name: str = "final_short.mp4",
) -> MicroJumpscareResult:
    """Mux single lunge clip + loud horror sting → browser-playable Short."""
    clips_dir = pack_dir / "clips"
    clip = clip_path or (clips_dir / "blender_part_01.mp4")
    if not clip.is_file() or clip.stat().st_size < 5000:
        raise FileNotFoundError(f"Micro jumpscare clip missing: {clip}")

    duration = _probe_duration(clip)
    sting_at = min(
        max(0.25, settings.micro_jumpscare_sting_at),
        max(0.25, duration - 0.35),
    )

    silent = pack_dir / "_micro_silent.mp3"
    _create_near_silent_bed(duration, silent)
    cues = [
        SfxCue(start_seconds=sting_at, kind="stinger", gain=1.35),
        SfxCue(start_seconds=sting_at + 0.006, kind="stinger_noise", gain=1.15),
        SfxCue(start_seconds=sting_at + 0.018, kind="metal_hit", gain=1.05),
    ]
    audio_path = mix_horror_sfx_into_voiceover(
        silent, cues, output_path=pack_dir / "_micro_stung.mp3"
    )
    (pack_dir / "sfx_cues.json").write_text(
        json.dumps(
            [{"start": c.start_seconds, "kind": c.kind, "gain": c.gain} for c in cues],
            indent=2,
        ),
        encoding="utf-8",
    )

    out_path = pack_dir / output_name
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(clip),
            "-i",
            str(audio_path),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-preset",
            settings.video_preset,
            "-crf",
            str(settings.video_crf),
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            f"{settings.video_audio_bitrate_k}k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            "-t",
            f"{duration:.3f}",
            str(out_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    manifest_path = pack_dir / "manifest.json"
    manifest: dict = {}
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(
        {
            "draft_id": draft_id,
            "render_mode": "micro_jumpscare",
            "content_format": "micro_jumpscare",
            "video_backend": "blender",
            "clips_rendered": 1,
            "micro_jumpscare": {
                "seconds": duration,
                "sting_at": sting_at,
                "volume_warning": "🔊 VOLUME WARNING — 3s jumpscare. Headphones.",
            },
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    meta_path = pack_dir / "upload_metadata.json"
    meta: dict = {}
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta.update(
        {
            "title": "🔊 3-Second Jumpscare — Peripheral",
            "description": (
                "🔊 VOLUME WARNING — sudden jumpscare in 3 seconds. Use headphones.\n\n"
                "Peripheral horror Shorts — don't blink.\n"
                "#horror #jumpscare #shorts"
            ),
            "tags": ["horror", "jumpscare", "shorts", "peripheral", "scary"],
        }
    )
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return MicroJumpscareResult(
        output_path=out_path,
        duration_seconds=duration,
        sting_at=sting_at,
        message=f"Micro jumpscare ready — {out_path.name} ({duration:.1f}s, sting @{sting_at:.2f}s)",
    )
