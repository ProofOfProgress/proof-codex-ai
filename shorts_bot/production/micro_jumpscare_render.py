"""Assemble 3s micro-jumpscare Short — single Blender lunge + loud horror bed + CC0 roar."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings


@dataclass
class MicroJumpscareResult:
    output_path: Path
    duration_seconds: float
    sting_at: float
    message: str


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_micro_roar_path() -> Path:
    """CC0 premade roar — safe for monetized YouTube Shorts."""
    path = settings.micro_jumpscare_roar_path
    if not path.is_absolute():
        path = _workspace_root() / path
    if not path.is_file():
        raise FileNotFoundError(
            f"Micro jumpscare roar missing: {path} "
            "(see channel/assets/sfx/ATTRIBUTION.txt)"
        )
    return path


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


def _create_micro_horror_audio(duration: float, roar_at: float, dest: Path) -> Path:
    """
    Loud horror bed throughout + CC0 premade monster roar at lunge
    + high-pitched scream at the final frame.
    """
    dur = max(1.0, float(duration))
    roar = min(max(0.2, roar_at), dur - 0.15)
    bed = settings.micro_jumpscare_bed_gain
    roar_gain = settings.micro_jumpscare_roar_gain
    delay_ms = int(roar * 1000)
    roar_file = resolve_micro_roar_path()
    dest.parent.mkdir(parents=True, exist_ok=True)

    scream_at = max(0.2, dur - settings.micro_jumpscare_scream_before_end)
    scream_ms = int(scream_at * 1000)
    scream_gain = settings.micro_jumpscare_scream_gain

    drone = (
        f"aevalsrc='{bed * 0.55}*sin(2*PI*43*t)+{bed * 0.38}*sin(2*PI*67*t)+"
        f"{bed * 0.22}*sin(2*PI*91*t)':d={dur:.3f}:sample_rate=48000"
    )
    static = (
        f"anoisesrc=color=white:duration={dur:.3f}:sample_rate=48000,"
        f"bandpass=f=900:w=4200,volume={bed * 0.42},"
        "afade=t=in:st=0:d=0.02"
    )
    rumble = (
        f"anoisesrc=color=brown:duration={dur:.3f}:sample_rate=48000,"
        f"lowpass=f=180,highpass=f=28,volume={bed * 0.65}"
    )
    # High-pitch shriek — layered sines + noise, peaks at final ~0.5s
    scream = (
        "aevalsrc="
        "'0.62*sin(2*PI*880*t)*exp(-3.5*t)+0.48*sin(2*PI*1320*t)*exp(-4.2*t)+"
        "0.35*sin(2*PI*1760*t)*exp(-5*t)+0.18*sin(2*PI*2200*t)*exp(-6*t)'"
        ":d=0.95:sample_rate=48000,"
        f"volume={scream_gain:.2f},highpass=f=520,tremolo=f=32:d=0.7,"
        "afade=t=in:st=0:d=0.015,afade=t=out:st=0.62:d=0.28"
    )

    inputs = ["[0:a][1:a][2:a]amix=inputs=3:duration=first:dropout_transition=0:normalize=0[bed]"]
    next_idx = 4
    maps = ["[bed]"]

    roar_chain = (
        f"[3:a]atrim=0:1.45,asetpts=PTS-STARTPTS,volume={roar_gain:.2f},"
        "afade=t=in:st=0:d=0.02,afade=t=out:st=1.15:d=0.25[roar];"
        f"[roar]adelay={delay_ms}|{delay_ms}[roar_d]"
    )
    inputs.append(roar_chain)
    maps.append("[roar_d]")

    if settings.micro_jumpscare_scream_enabled:
        scream_chain = (
            f"[{next_idx}:a]asetpts=PTS-STARTPTS[scream];"
            f"[scream]adelay={scream_ms}|{scream_ms}[scream_d]"
        )
        inputs.append(scream_chain)
        maps.append("[scream_d]")

    mix_n = len(maps)
    filter_complex = (
        ";".join(inputs)
        + ";"
        + "".join(maps)
        + f"amix=inputs={mix_n}:duration=first:dropout_transition=0:normalize=0[out]"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        drone,
        "-f",
        "lavfi",
        "-i",
        static,
        "-f",
        "lavfi",
        "-i",
        rumble,
        "-i",
        str(roar_file),
    ]
    if settings.micro_jumpscare_scream_enabled:
        cmd.extend(["-f", "lavfi", "-i", scream])
    cmd.extend(
        [
            "-filter_complex",
            filter_complex,
            "-map",
            "[out]",
            "-c:a",
            "libmp3lame",
            "-b:a",
            f"{settings.video_audio_bitrate_k}k",
            str(dest),
        ]
    )

    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return dest


def render_micro_jumpscare_final(
    pack_dir: Path,
    *,
    draft_id: int,
    clip_path: Path | None = None,
    output_name: str = "final_short.mp4",
    motion_source: str = "procedural_learned",
) -> MicroJumpscareResult:
    """Mux single lunge clip + loud horror bed + CC0 roar → browser-playable Short."""
    clips_dir = pack_dir / "clips"
    clip = clip_path or (clips_dir / "blender_part_01.mp4")
    if not clip.is_file() or clip.stat().st_size < 5000:
        raise FileNotFoundError(f"Micro jumpscare clip missing: {clip}")

    duration = _probe_duration(clip)
    # Roar at bait; high scream lands on final lunge frame
    roar_at = min(
        max(0.25, settings.micro_jumpscare_sting_at),
        max(0.25, duration - 0.35),
    )
    scream_at = max(0.2, duration - settings.micro_jumpscare_scream_before_end)

    audio_path = pack_dir / "_micro_horror.mp3"
    roar_path = resolve_micro_roar_path()
    _create_micro_horror_audio(duration, roar_at, audio_path)
    cues = [
        {"start": 0.0, "kind": "horror_bed_drone", "gain": settings.micro_jumpscare_bed_gain},
        {"start": 0.0, "kind": "horror_bed_static", "gain": settings.micro_jumpscare_bed_gain},
        {"start": 0.0, "kind": "horror_bed_rumble", "gain": settings.micro_jumpscare_bed_gain},
        {
            "start": roar_at,
            "kind": "creature_roar_cc0",
            "gain": settings.micro_jumpscare_roar_gain,
            "file": str(roar_path.name),
        },
    ]
    if settings.micro_jumpscare_scream_enabled:
        cues.append(
            {
                "start": scream_at,
                "kind": "high_pitch_scream",
                "gain": settings.micro_jumpscare_scream_gain,
            }
        )
    (pack_dir / "sfx_cues.json").write_text(json.dumps(cues, indent=2), encoding="utf-8")

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
                "roar_at": roar_at,
                "scream_at": scream_at if settings.micro_jumpscare_scream_enabled else None,
                "roar_asset": roar_path.name,
                "motion_source": motion_source,
                "framing": "face_upper_third_locked_camera",
                "volume_warning": "🔊 VOLUME WARNING — loud 3s jumpscare + creature roar + scream. Headphones.",
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
                "🔊 VOLUME WARNING — loud horror audio + creature roar. Use headphones.\n\n"
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
        sting_at=roar_at,
        message=(
            f"Micro jumpscare ready — {out_path.name} ({duration:.1f}s, "
            f"CC0 roar @{roar_at:.2f}s, scream @{scream_at:.2f}s)"
        ),
    )
