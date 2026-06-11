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


def _ken_burns_zoompan(duration: float, *, zoom_motion: str, width: int, height: int) -> str:
    """Subtle zoom per still — retention lift without CapCut."""
    frames = max(1, int(duration * 30))
    if zoom_motion == "out":
        z = "if(lte(zoom,1.0),1.06,max(1.001,zoom-0.0004))"
    elif zoom_motion == "in":
        z = "min(zoom+0.0004,1.06)"
    else:
        return f"scale={width}:{height}:flags=lanczos,format=yuv420p"
    return (
        f"scale={width}:{height}:flags=lanczos,"
        f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={width}x{height}:fps=30,format=yuv420p"
    )


def _render_motion_clips(
    images_dir: Path,
    segments: list[dict],
    durations: list[float],
    *,
    zoom_motion: str,
    tmp_dir: Path,
    width: int,
    height: int,
) -> Path:
    """Pre-render each still to a short MP4 with optional Ken Burns."""
    tmp_dir.mkdir(parents=True, exist_ok=True)
    clip_paths: list[Path] = []
    for i, (seg, dur) in enumerate(zip(segments, durations)):
        img = images_dir / seg["filename"]
        clip = tmp_dir / f"clip_{i:03d}.mp4"
        vf = _ken_burns_zoompan(dur, zoom_motion=zoom_motion, width=width, height=height)
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-t",
                f"{dur:.4f}",
                "-i",
                str(img.resolve()),
                "-vf",
                vf,
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-pix_fmt",
                "yuv420p",
                "-an",
                str(clip),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        clip_paths.append(clip)

    concat_path = tmp_dir / "_clips_concat.txt"
    lines = ["ffconcat version 1.0"]
    for clip in clip_paths:
        lines.append(f"file '{clip.resolve()}'")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    silent_video = tmp_dir / "_video_silent.mp4"
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
            str(silent_video),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return silent_video



def _trim_scale_clip(
    src: Path,
    dest: Path,
    *,
    duration: float,
    width: int,
    height: int,
) -> None:
    vf = f"scale={width}:{height}:flags=lanczos,format=yuv420p"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src.resolve()),
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


def _render_from_video_clips(
    clips_dir: Path,
    segments: list[dict],
    durations: list[float],
    *,
    tmp_dir: Path,
    width: int,
    height: int,
) -> Path:
    tmp_dir.mkdir(parents=True, exist_ok=True)
    clip_paths: list[Path] = []
    for i, (seg, dur) in enumerate(zip(segments, durations)):
        stem = Path(seg["filename"]).stem
        src = clips_dir / f"{stem}.mp4"
        if not src.exists():
            raise FileNotFoundError(f"Missing motion clip: {src}")
        clip = tmp_dir / f"clip_{i:03d}.mp4"
        _trim_scale_clip(src, clip, duration=dur, width=width, height=height)
        clip_paths.append(clip)
    concat_path = tmp_dir / "_clips_concat.txt"
    lines = ["ffconcat version 1.0"]
    for clip in clip_paths:
        lines.append(f"file '{clip.resolve()}'")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    silent_video = tmp_dir / "_video_silent.mp4"
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
            str(silent_video),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return silent_video


def render_short_video(
    pack_dir: Path,
    *,
    draft_id: int,
    audio_name: str = "voiceover.mp3",
    output_name: str = "final_short.mp4",
    caption_y_offset: int = 0,
    zoom_motion: str = "none",
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

    out_path = pack_dir / output_name

    from shorts_bot.config import settings
    from shorts_bot.production.captions import burn_captions_via_ffmpeg
    from shorts_bot.production.subtitles import ffmpeg_subtitles_filter, write_subtitle_files

    ass_path = write_subtitle_files(
        pack_dir,
        segments,
        audio_duration,
        caption_y_offset=caption_y_offset,
    )

    from shorts_bot.production.framing import FRAME_HEIGHT, FRAME_WIDTH

    render_mode = manifest.get("render_mode") or "slideshow"
    if render_mode == "video_clips":
        clips_dir = pack_dir / "clips"
        silent = _render_from_video_clips(
            clips_dir,
            segments,
            durations,
            tmp_dir=pack_dir / "_motion_clips",
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
        )
        video_input = ["-i", str(silent)]
        vf_parts: list[str] = []
        if burn_captions_via_ffmpeg() or settings.burn_in_subtitles:
            vf_parts.append(ffmpeg_subtitles_filter(ass_path).split(",", 1)[1])
        vf = ",".join(vf_parts) if vf_parts else None
        cmd = ["ffmpeg", "-y", *video_input, "-i", str(audio_path)]
        if vf:
            cmd.extend(["-vf", vf])
        cmd.extend(
            [
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
                f"{audio_duration:.3f}",
                str(out_path),
            ]
        )
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return RenderedVideo(
            draft_id=draft_id,
            output_path=out_path,
            duration_seconds=audio_duration,
            message=(
                f"Rendered {out_path.name} ({audio_duration:.1f}s, 1080×1920, AI video clips). "
                f"Captions: ffmpeg ASS burn-in + captions.srt for YouTube."
            ),
        )

    use_motion = settings.video_ken_burns and zoom_motion in ("in", "out")
    if use_motion:
        silent = _render_motion_clips(
            images_dir,
            segments,
            durations,
            zoom_motion=zoom_motion,
            tmp_dir=pack_dir / "_motion_clips",
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
        )
        video_input = ["-i", str(silent)]
    else:
        concat_path = pack_dir / "_concat.txt"
        _write_concat(images_dir, segments, durations, concat_path)
        video_input = ["-f", "concat", "-safe", "0", "-i", str(concat_path)]

    vf_parts: list[str] = []
    if not use_motion:
        vf_parts.extend([f"scale={FRAME_WIDTH}:{FRAME_HEIGHT}:flags=lanczos", "format=yuv420p"])
    if burn_captions_via_ffmpeg() or settings.burn_in_subtitles:
        vf_parts.append(ffmpeg_subtitles_filter(ass_path).split(",", 1)[1])
    vf = ",".join(vf_parts) if vf_parts else None

    cmd = ["ffmpeg", "-y", *video_input, "-i", str(audio_path)]
    if vf:
        cmd.extend(["-vf", vf])
    cmd.extend(
        [
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
            f"{audio_duration:.3f}",
            str(out_path),
        ]
    )
    subprocess.run(cmd, check=True, capture_output=True, text=True)

    return RenderedVideo(
        draft_id=draft_id,
        output_path=out_path,
        duration_seconds=audio_duration,
        message=(
            f"Rendered {out_path.name} ({audio_duration:.1f}s, 1080×1920"
            f"{', Ken Burns ' + zoom_motion if use_motion else ''}). "
            f"Captions: ffmpeg ASS burn-in + captions.srt for YouTube."
        ),
    )
