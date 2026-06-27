"""Module 6 affiliate edit — on-screen caption burn (white box / black text)."""

from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

DEFAULT_FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def wrap_on_screen_caption(text: str, *, max_chars: int = 38) -> str:
    """Break hook copy into lines for upper-third burn-in."""
    clean = " ".join((text or "").split())
    if not clean:
        return ""
    return "\n".join(textwrap.wrap(clean, width=max_chars, break_long_words=False, break_on_hyphens=False))


def burn_on_screen_caption(
    source: Path,
    dest: Path,
    text: str,
    *,
    font_path: Path | None = None,
    font_size: int = 46,
    y_fraction: float = 0.11,
) -> Path:
    """
    Burn Module 6 caption — bold black text, white box, upper-center.
    Course: module_06_editing.md + VIDEO_EDITOR.md
    """
    wrapped = wrap_on_screen_caption(text)
    if not wrapped:
        raise ValueError("on-screen caption text is required")
    if not source.is_file():
        raise FileNotFoundError(source)

    font = font_path or DEFAULT_FONT
    if not font.is_file():
        raise RuntimeError(f"Caption font missing: {font}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    text_file = dest.with_suffix(".caption.txt")
    text_file.write_text(wrapped, encoding="utf-8")

    # ffmpeg filter paths — escape for drawtext
    tf = str(text_file.resolve()).replace("\\", "/").replace(":", "\\:")
    ff = str(font.resolve()).replace("\\", "/").replace(":", "\\:")
    vf = (
        f"drawtext=fontfile='{ff}':textfile='{tf}':"
        f"fontsize={font_size}:fontcolor=black:"
        f"box=1:boxcolor=white@0.92:boxborderw=18:"
        f"x=(w-text_w)/2:y=h*{y_fraction}"
    )
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
        "20",
        "-pix_fmt",
        "yuv420p",
        str(dest),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    text_file.unlink(missing_ok=True)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-800:]
        raise RuntimeError(f"ffmpeg caption burn failed: {tail}")
    return dest
