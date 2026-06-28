"""Module 6 affiliate edit — on-screen caption burn (white text, black outline)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.captions import wrap_hook_text

DEFAULT_FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def wrap_on_screen_caption(text: str, *, max_chars_per_line: int | None = None) -> str:
    """Break hook copy into lines — default max 26 chars per line (owner rule)."""
    return wrap_hook_text(text, max_chars_per_line=max_chars_per_line)


def burn_on_screen_caption(
    source: Path,
    dest: Path,
    text: str,
    *,
    font_path: Path | None = None,
    font_size: int | None = None,
    y_fraction: float = 0.11,
    outline_width: int = 2,
) -> Path:
    """
    Burn Module 6 caption — bold white text, tiny black outline, no background bubble.
    Owner override: VIDEO_EDITOR.md
    """
    wrapped = wrap_on_screen_caption(text)
    if not wrapped:
        raise ValueError("on-screen caption text is required")
    if not source.is_file():
        raise FileNotFoundError(source)

    font = font_path or DEFAULT_FONT
    if not font.is_file():
        raise RuntimeError(f"Caption font missing: {font}")

    size = font_size if font_size is not None else settings.tiktok_shop_caption_font_size

    dest.parent.mkdir(parents=True, exist_ok=True)
    text_file = dest.with_suffix(".caption.txt")
    text_file.write_text(wrapped, encoding="utf-8")

    tf = str(text_file.resolve()).replace("\\", "/").replace(":", "\\:")
    ff = str(font.resolve()).replace("\\", "/").replace(":", "\\:")
    vf = (
        f"drawtext=fontfile='{ff}':textfile='{tf}':"
        f"fontsize={size}:fontcolor=white:"
        f"borderw={outline_width}:bordercolor=black:"
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
