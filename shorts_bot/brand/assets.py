"""Generate channel profile + banner PNGs — The Minute Before visual system."""

from __future__ import annotations

import math
from pathlib import Path

ASSETS_DIR = Path("channel/brand/assets")
PROFILE_PATH = ASSETS_DIR / "profile.png"
BANNER_PATH = ASSETS_DIR / "banner.png"

# identity.md palette
BG_TOP = "#0B0D10"
BG_MID = "#141820"
ACCENT_BLUE = "#8EB8FF"
ACCENT_PURPLE = "#C4A1FF"
TEXT_PRIMARY = "#F2F5FA"
TEXT_MUTED = "#9AA8BC"


def _load_fonts(size_lg: int, size_md: int, size_sm: int):
    from PIL import ImageFont

    candidates_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    candidates_reg = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    font_lg = font_md = font_sm = ImageFont.load_default()
    for path in candidates_bold:
        try:
            font_lg = ImageFont.truetype(path, size_lg)
            font_md = ImageFont.truetype(path, size_md)
            break
        except OSError:
            continue
    for path in candidates_reg:
        try:
            font_sm = ImageFont.truetype(path, size_sm)
            break
        except OSError:
            continue
    return font_lg, font_md, font_sm


def _hex_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _vertical_gradient(img, top: str, bottom: str) -> None:
    from PIL import ImageDraw

    w, h = img.size
    draw = ImageDraw.Draw(img)
    t = _hex_rgb(top)
    b = _hex_rgb(bottom)
    for y in range(h):
        ratio = y / max(h - 1, 1)
        color = tuple(int(t[i] + (b[i] - t[i]) * ratio) for i in range(3))
        draw.line([(0, y), (w, y)], fill=color)


def _draw_clock_face(draw, cx: int, cy: int, radius: int, *, minute_before: bool = True) -> None:
    """Minimal dial — hands near 11:59 (the minute before)."""
    blue = _hex_rgb(ACCENT_BLUE)
    purple = _hex_rgb(ACCENT_PURPLE)
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        outline=blue,
        width=max(3, radius // 80),
    )
    draw.ellipse(
        [cx - radius + 18, cy - radius + 18, cx + radius - 18, cy + radius - 18],
        outline=purple,
        width=2,
    )
    for hour in range(12):
        angle = math.radians(hour * 30 - 90)
        inner = radius - 22
        outer = radius - 8
        x1 = cx + inner * math.cos(angle)
        y1 = cy + inner * math.sin(angle)
        x2 = cx + outer * math.cos(angle)
        y2 = cy + outer * math.sin(angle)
        draw.line([(x1, y1), (x2, y2)], fill=blue, width=2)

    if minute_before:
        # Hour hand ~11, minute hand ~58
        hour_angle = math.radians(11 * 30 - 90)
        min_angle = math.radians(58 * 6 - 90)
        hx = cx + (radius * 0.45) * math.cos(hour_angle)
        hy = cy + (radius * 0.45) * math.sin(hour_angle)
        mx = cx + (radius * 0.62) * math.cos(min_angle)
        my = cy + (radius * 0.62) * math.sin(min_angle)
        draw.line([(cx, cy), (hx, hy)], fill=TEXT_PRIMARY, width=max(4, radius // 45))
        draw.line([(cx, cy), (mx, my)], fill=ACCENT_BLUE, width=max(3, radius // 55))
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=purple)


def generate_profile_image(out_path: Path | None = None) -> Path:
    """800×800 profile — clock at the minute before, readable at avatar size."""
    from PIL import Image, ImageDraw

    out = out_path or PROFILE_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    size = 800
    img = Image.new("RGB", (size, size), BG_TOP)
    _vertical_gradient(img, BG_TOP, BG_MID)
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    # Outer glow rings
    for r, alpha_color in (
        (360, ACCENT_PURPLE),
        (320, ACCENT_BLUE),
    ):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=alpha_color, width=3)

    _draw_clock_face(draw, cx, cy, 250, minute_before=True)

    # Tiny series mark (legible on mobile)
    font_sm = _load_fonts(28, 24, 20)[2]
    label = "1 min"
    tw = draw.textlength(label, font=font_sm) if hasattr(draw, "textlength") else 60
    draw.text((cx - tw / 2, cy + 290), label, fill=TEXT_MUTED, font=font_sm)

    img.save(out, "PNG", optimize=True)
    return out


def generate_banner_image(out_path: Path | None = None) -> Path:
    """2560×1440 banner — Minute Before hero, YouTube safe-zone centered."""
    from PIL import Image, ImageDraw

    out = out_path or BANNER_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    w, h = 2560, 1440
    img = Image.new("RGB", (w, h), BG_TOP)
    _vertical_gradient(img, BG_TOP, "#1A1428")
    draw = ImageDraw.Draw(img)

    cx, cy = w // 2, int(h * 0.46)
    for r in (220, 270, 320):
        draw.ellipse(
            [cx - r, cy - r - 40, cx + r, cy + r - 40],
            outline=ACCENT_BLUE if r == 220 else ACCENT_PURPLE,
            width=3 if r == 220 else 1,
        )

    font_lg, font_md, font_sm = _load_fonts(128, 52, 40)

    eyebrow = "DON'T BLINK"
    title = "Watch the whole thing."
    sub = "terrifying horror Shorts · jumpscare at the end"
    tag = "🔊 volume warning"

    ew = draw.textlength(eyebrow, font=font_sm) if hasattr(draw, "textlength") else 700
    draw.text(((w - ew) / 2, h * 0.30), eyebrow, fill=TEXT_MUTED, font=font_sm)

    tw = draw.textlength(title, font=font_lg) if hasattr(draw, "textlength") else 1200
    draw.text(((w - tw) / 2, h * 0.38), title, fill=TEXT_PRIMARY, font=font_lg)

    sw = draw.textlength(sub, font=font_md) if hasattr(draw, "textlength") else 1100
    draw.text(((w - sw) / 2, h * 0.52), sub, fill=ACCENT_BLUE, font=font_md)

    pillars = "conversations · work dread · boundaries · after the slip"
    pw = draw.textlength(pillars, font=font_sm) if hasattr(draw, "textlength") else 900
    draw.text(((w - pw) / 2, h * 0.60), pillars, fill=TEXT_MUTED, font=font_sm)

    gw = draw.textlength(tag, font=font_sm) if hasattr(draw, "textlength") else 500
    draw.text(((w - gw) / 2, h * 0.68), tag, fill=ACCENT_PURPLE, font=font_sm)

    img.save(out, "PNG", optimize=True)
    return out


def ensure_brand_assets() -> tuple[Path, Path]:
    """Return Don't Blink eye assets; use committed PNGs when present."""
    if PROFILE_PATH.exists() and BANNER_PATH.exists():
        return PROFILE_PATH, BANNER_PATH
    return generate_profile_image(), generate_banner_image()
