"""Bottom caption bar for mute-safe Short frames (Jenny 05)."""

from __future__ import annotations

import textwrap


def _font_reg(size: int):
    from PIL import ImageFont

    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def draw_bottom_caption(draw, text: str, w: int, h: int) -> None:
    font = _font_reg(36)
    lines = textwrap.wrap(" ".join(text.split()), width=28)[:2]
    if not lines:
        return
    line_h = 44
    pad = 20
    bar_h = len(lines) * line_h + pad * 2
    by = h - bar_h - 80
    draw.rounded_rectangle([40, by, w - 40, by + bar_h], radius=14, fill="#111111", outline="#111111")
    y = by + pad
    for ln in lines:
        tw = draw.textlength(ln, font=font) if hasattr(draw, "textlength") else len(ln) * 18
        draw.text(((w - tw) / 2, y), ln, fill="#FFFFFF", font=font)
        y += line_h


def apply_bottom_caption(image_path, spoken_text: str, *, width: int = 1080, height: int = 1920) -> None:
    """Open image, ensure 9:16, draw caption bar, save PNG."""
    from PIL import Image, ImageDraw

    img = Image.open(image_path).convert("RGB")
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)
    draw_bottom_caption(draw, spoken_text, width, height)
    img.save(image_path, "PNG")
