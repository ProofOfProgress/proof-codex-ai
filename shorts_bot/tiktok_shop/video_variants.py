"""Video variants — motion-enhanced loop (~10s) from 5s Kling raw."""

from __future__ import annotations

import subprocess
from pathlib import Path

from shorts_bot.config import settings


def build_motion_enhance_vf(
    *,
    lateral_amplitude: float | None = None,
    micro_shake_px: float | None = None,
) -> str:
    """
    FFmpeg filter: ~25% more side-to-side travel + micro-shake (Momentum coach 2026-06-29).

    Applied in Module 6 post so TikTok's still-frame detector sees parallax even when
    Kling arc motion is subtle.
    """
    lat = settings.pan_loop_lateral_amplitude if lateral_amplitude is None else lateral_amplitude
    shake = settings.pan_loop_micro_shake_px if micro_shake_px is None else micro_shake_px
    crop_w = max(0.75, min(0.95, 1.0 - lat * 0.12))
    return (
        f"crop=w='floor(iw*{crop_w})':h=ih:"
        f"x='(iw-ow)/2+{lat}*iw*sin(2*PI*t/5)+{shake}*sin(2*PI*t*8)':"
        f"y='{shake}*sin(2*PI*t*7)',"
        "scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1"
    )


def apply_motion_enhance(source: Path, dest: Path) -> Path:
    """Re-encode with lateral pan + micro-shake."""
    if not source.is_file():
        raise FileNotFoundError(source)
    dest.parent.mkdir(parents=True, exist_ok=True)
    vf = build_motion_enhance_vf()
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-vf",
        vf,
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        str(dest),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-800:]
        raise RuntimeError(f"ffmpeg motion enhance failed: {tail}")
    return dest


def mean_inter_frame_motion(frames: list[Path], *, sample_size: tuple[int, int] = (270, 480)) -> float:
    """
    Mean normalized pixel delta between consecutive JPEG frames (0 = identical still).
    Used by Module 1 QC still-frame gate.
    """
    if len(frames) < 2:
        return 0.0
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow required for motion score") from exc

    prev_pixels: list[int] | None = None
    diffs: list[float] = []
    w, h = sample_size
    for path in frames:
        if not path.is_file():
            continue
        gray = Image.open(path).convert("L").resize((w, h))
        pixels = list(gray.getdata())
        if prev_pixels is not None and len(pixels) == len(prev_pixels):
            total = sum(abs(a - b) for a, b in zip(pixels, prev_pixels))
            diffs.append(total / (255.0 * len(pixels)))
        prev_pixels = pixels
    if not diffs:
        return 0.0
    return sum(diffs) / len(diffs)


def make_pan_loop_clip(source: Path, dest: Path, *, enhance_motion: bool | None = None) -> Path:
    """
    Motion-enhance 5s Kling clip, then forward + reverse concat → ~10s loop.
    Requires ffmpeg on PATH.
    """
    if not source.is_file():
        raise FileNotFoundError(source)
    dest.parent.mkdir(parents=True, exist_ok=True)

    do_enhance = settings.pan_loop_motion_enhance if enhance_motion is None else enhance_motion
    working = source
    motion_tmp: Path | None = None
    if do_enhance:
        motion_tmp = dest.with_name(dest.stem + "_motion.mp4")
        apply_motion_enhance(source, motion_tmp)
        working = motion_tmp

    rev = dest.with_name(dest.stem + "_rev.mp4")
    cmd_rev = ["ffmpeg", "-y", "-i", str(working), "-vf", "reverse", "-an", str(rev)]
    proc_rev = subprocess.run(cmd_rev, capture_output=True, text=True)
    if proc_rev.returncode != 0:
        if motion_tmp and motion_tmp.is_file():
            motion_tmp.unlink(missing_ok=True)
        tail = (proc_rev.stderr or proc_rev.stdout or "")[-800:]
        raise RuntimeError(f"ffmpeg reverse failed: {tail}")

    list_file = dest.with_suffix(".txt")
    list_file.write_text(f"file '{working.resolve()}'\nfile '{rev.resolve()}'\n", encoding="utf-8")
    cmd_cat = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-c",
        "copy",
        str(dest),
    ]
    proc_cat = subprocess.run(cmd_cat, capture_output=True, text=True)
    if proc_cat.returncode != 0:
        tail = (proc_cat.stderr or proc_cat.stdout or "")[-800:]
        raise RuntimeError(f"ffmpeg concat failed: {tail}")

    if rev.is_file():
        rev.unlink(missing_ok=True)
    if motion_tmp and motion_tmp.is_file():
        motion_tmp.unlink(missing_ok=True)
    list_file.unlink(missing_ok=True)
    return dest
