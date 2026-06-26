"""Caption layout copied from owner sample slide positions (bubble wrap7 + wrap10)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Reference sample dimensions (owner Drive PNGs)
REF_HOOK = Path("data/research/course/_media/bubble_wrap/samples/bubble wrap7.png")
REF_CTA = Path("data/research/course/_media/bubble_wrap/samples/bubble wrap10.png")

OUTPUT_SIZE = (1080, 1920)  # TikTok 9:16

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


@dataclass(frozen=True)
class TextLine:
    text: str
    y_ratio: float  # vertical center of line, 0–1


# Positions measured from owner hook sample (bubble wrap7) — centered 2-line block
HOOK_LINES = (
    TextLine("ORANGE BUBBLE WRAP", 0.46),
    TextLine("ASMR >>>", 0.54),
)

# Positions measured from owner CTA sample (bubble wrap10) — centered 4-line block
CTA_LINES = (
    TextLine("Pause = Pop 💥", 0.36),
    TextLine("Follow = Loud pop 🔊", 0.44),
    TextLine("Share = Giant pop 🦖", 0.52),
    TextLine("Comment = Big pop 💥💥", 0.60),
)


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD, size)


def _fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    *,
    max_width: int,
    start_size: int,
    min_size: int = 28,
) -> ImageFont.FreeTypeFont:
    size = start_size
    while size >= min_size:
        font = _font(size)
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font
        size -= 2
    return _font(min_size)


def _draw_stroked_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    *,
    y: int,
    width: int,
    font: ImageFont.FreeTypeFont,
    fill: str = "white",
    stroke: str = "black",
    stroke_width: int = 6,
    use_pilmoji: bool = False,
    img: Image.Image | None = None,
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (width - tw) // 2
    y0 = y - th // 2
    if use_pilmoji and img is not None:
        from pilmoji import Pilmoji

        with Pilmoji(img) as pilmoji:
            pilmoji.text(
                (x, y0),
                text,
                font=font,
                fill=fill,
                stroke_width=stroke_width,
                stroke_fill=stroke,
            )
        return
    draw.text((x, y0), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke)


def compose_hook_slide(base: Path, out: Path) -> None:
    img = Image.open(base).convert("RGB")
    img = img.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)
    w, h = img.size
    max_w = int(w * 0.92)
    for line in HOOK_LINES:
        font = _fit_font(draw, line.text, max_width=max_w, start_size=int(h * 0.055))
        _draw_stroked_centered(draw, line.text, y=int(h * line.y_ratio), width=w, font=font)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG", optimize=True)


def compose_cta_slide(base: Path, out: Path) -> None:
    img = Image.open(base).convert("RGB")
    img = img.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)
    w, h = img.size
    max_w = int(w * 0.92)
    probe = ImageDraw.Draw(img)

    from pilmoji import Pilmoji

    with Pilmoji(img) as pilmoji:
        for line in CTA_LINES:
            font = _fit_font(probe, line.text, max_width=max_w, start_size=int(h * 0.042))
            bbox = probe.textbbox((0, 0), line.text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            x = (w - tw) // 2
            y0 = int(h * line.y_ratio) - th // 2
            pilmoji.text(
                (x, y0),
                line.text,
                font=font,
                fill="white",
                stroke_width=5,
                stroke_fill="black",
            )
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG", optimize=True)
