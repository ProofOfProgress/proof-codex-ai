"""Frame caption bar — PIL fallback when caption_mode=frame (Jenny 05 safe zone)."""

from __future__ import annotations

from shorts_bot.production.captions import format_caption_lines
from shorts_bot.production.framing import (
    CAPTION_FONT_SIZE,
    CAPTION_LINE_HEIGHT,
    CAPTION_SIDE_MARGIN_PX,
    caption_bar_y,
)


def _font_bold(size: int):
    from PIL import ImageFont

    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _line_width(draw, text: str, font) -> float:
    if hasattr(draw, "textlength"):
        return float(draw.textlength(text, font=font))
    bbox = draw.textbbox((0, 0), text, font=font)
    return float(bbox[2] - bbox[0])


def draw_bottom_caption(draw, text: str, w: int, h: int) -> None:
    """Draw rounded bar + centered text using pixel-aware wrapping."""
    font = _font_bold(CAPTION_FONT_SIZE)
    max_px = w - CAPTION_SIDE_MARGIN_PX * 2 - 48
    lines = format_caption_lines(text)

    # Shrink lines that exceed pixel width
    fitted: list[str] = []
    for ln in lines:
        if _line_width(draw, ln, font) <= max_px:
            fitted.append(ln)
            continue
        words = ln.split()
        chunk: list[str] = []
        for word in words:
            trial = " ".join([*chunk, word])
            if _line_width(draw, trial, font) <= max_px:
                chunk.append(word)
            else:
                if chunk:
                    fitted.append(" ".join(chunk))
                    chunk = [word]
                else:
                    fitted.append(word[:18] + "…")
                    chunk = []
        if chunk and len(fitted) < 2:
            fitted.append(" ".join(chunk))

    lines = fitted[:2]
    if not lines:
        return

    line_h = CAPTION_LINE_HEIGHT
    pad = 20
    bar_h = len(lines) * line_h + pad * 2
    by = caption_bar_y(bar_h, frame_height=h)

    draw.rounded_rectangle(
        [CAPTION_SIDE_MARGIN_PX, by, w - CAPTION_SIDE_MARGIN_PX, by + bar_h],
        radius=14,
        fill="#141414",
        outline="#2A2A2A",
        width=1,
    )

    y = by + pad
    for ln in lines:
        tw = _line_width(draw, ln, font)
        x = (w - tw) / 2
        # subtle stroke for readability on bright stills
        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            draw.text((x + ox, y + oy), ln, fill="#000000", font=font)
        draw.text((x, y), ln, fill="#FFFFFF", font=font)
        y += line_h


def apply_bottom_caption(image_path, spoken_text: str, *, width: int = 1080, height: int = 1920) -> None:
    """Open image, ensure 9:16, draw caption bar, save PNG."""
    from PIL import Image, ImageDraw

    img = Image.open(image_path).convert("RGB")
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)
    draw_bottom_caption(draw, spoken_text, width, height)
    img.save(image_path, "PNG")
