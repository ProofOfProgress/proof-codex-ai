"""Bottom caption bar for mute-safe Short frames (Jenny 05 safe zone).

Jenny Hoyos course file 05 — keep text in the safe zone; Shorts UI covers the bottom
~15–18% with title and buttons, so captions sit above that band (not flush to bottom).
"""

from __future__ import annotations

import textwrap

from shorts_bot.production.framing import (
    CAPTION_FONT_SIZE,
    CAPTION_LINE_HEIGHT,
    CAPTION_MAX_LINES,
    CAPTION_SIDE_MARGIN_PX,
    CAPTION_WRAP_WIDTH,
    caption_bar_y,
)


def _font_reg(size: int):
    from PIL import ImageFont

    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def draw_bottom_caption(draw, text: str, w: int, h: int) -> None:
    font = _font_reg(CAPTION_FONT_SIZE)
    lines = textwrap.wrap(" ".join(text.split()), width=CAPTION_WRAP_WIDTH)[:CAPTION_MAX_LINES]
    if not lines:
        return
    line_h = CAPTION_LINE_HEIGHT
    pad = 20
    bar_h = len(lines) * line_h + pad * 2
    by = caption_bar_y(bar_h, frame_height=h)
    draw.rounded_rectangle(
        [CAPTION_SIDE_MARGIN_PX, by, w - CAPTION_SIDE_MARGIN_PX, by + bar_h],
        radius=14,
        fill="#111111",
        outline="#111111",
    )
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
