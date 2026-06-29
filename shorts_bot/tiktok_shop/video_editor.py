"""Module 6 affiliate edit — on-screen caption burn (white text, black outline)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.captions import wrap_hook_lines

DEFAULT_FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def _escape_drawtext(text: str) -> str:
    """Escape user copy for ffmpeg drawtext single-quoted strings."""
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
    )


def build_centered_caption_filter(
    lines: list[str],
    *,
    font_path: Path,
    font_size: int,
    y_fraction: float = 0.11,
    outline_width: int = 2,
    line_spacing: float = 1.25,
) -> str:
    """One drawtext per line — each row centered (TikTok center align, not left rag)."""
    if not lines:
        raise ValueError("caption lines required")
    ff = str(font_path.resolve()).replace("\\", "/").replace(":", "\\:")
    step = max(1, int(font_size * line_spacing))
    filters: list[str] = []
    for i, line in enumerate(lines):
        escaped = _escape_drawtext(line)
        y_expr = f"h*{y_fraction}+{i * step}"
        filters.append(
            f"drawtext=fontfile='{ff}':text='{escaped}':"
            f"fontsize={font_size}:fontcolor=white:"
            f"borderw={outline_width}:bordercolor=black:"
            f"x=(w-text_w)/2:y={y_expr}"
        )
    return ",".join(filters)


def wrap_on_screen_caption(text: str, *, max_chars_per_line: int | None = None) -> str:
    """Break hook copy into lines — default max 20 chars per line (owner rule)."""
    return "\n".join(wrap_hook_lines(text, max_chars_per_line=max_chars_per_line))


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
    lines = [ln for ln in wrapped.splitlines() if ln.strip()]
    if not lines:
        raise ValueError("on-screen caption text is required")
    if not source.is_file():
        raise FileNotFoundError(source)

    font = font_path or DEFAULT_FONT
    if not font.is_file():
        raise RuntimeError(f"Caption font missing: {font}")

    size = font_size if font_size is not None else settings.tiktok_shop_caption_font_size

    dest.parent.mkdir(parents=True, exist_ok=True)
    vf = build_centered_caption_filter(
        lines,
        font_path=font,
        font_size=size,
        y_fraction=y_fraction,
        outline_width=outline_width,
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
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-800:]
        raise RuntimeError(f"ffmpeg caption burn failed: {tail}")
    return dest
