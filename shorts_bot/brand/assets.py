"""Generate channel profile + banner PNGs (no browser)."""

from __future__ import annotations

from pathlib import Path

ASSETS_DIR = Path("channel/brand/assets")
PROFILE_PATH = ASSETS_DIR / "profile.png"
BANNER_PATH = ASSETS_DIR / "banner.png"


def generate_profile_image(out_path: Path | None = None) -> Path:
    """800×800 profile — Soft Continuity halo ring on dark void."""
    from PIL import Image, ImageDraw

    out = out_path or PROFILE_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    size = 800
    img = Image.new("RGB", (size, size), "#0B0D10")
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    draw.ellipse([80, 80, size - 80, size - 80], outline="#8EB8FF", width=6)
    draw.ellipse([140, 140, size - 140, size - 140], outline="#C4A1FF", width=3)
    draw.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill="#141820", outline="#8EB8FF", width=2)
    img.save(out, "PNG")
    return out


def generate_banner_image(out_path: Path | None = None) -> Path:
    """2560×1440 banner — minimal brand strip."""
    from PIL import Image, ImageDraw

    out = out_path or BANNER_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    w, h = 2560, 1440
    img = Image.new("RGB", (w, h), "#0B0D10")
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(11 + t * 10)
        g = int(13 + t * 12)
        b = int(16 + t * 18)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    from PIL import ImageFont

    try:
        font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
    except OSError:
        font_lg = ImageFont.load_default()
        font_sm = ImageFont.load_default()

    title = "Soft Continuity"
    sub = "The Minute Before — one moment. one fix."
    tw = draw.textlength(title, font=font_lg) if hasattr(draw, "textlength") else 600
    draw.text(((w - tw) / 2, h * 0.38), title, fill="#F2F5FA", font=font_lg)
    sw = draw.textlength(sub, font=font_sm) if hasattr(draw, "textlength") else 800
    draw.text(((w - sw) / 2, h * 0.52), sub, fill="#8EB8FF", font=font_sm)
    draw.ellipse([w // 2 - 200, h * 0.62, w // 2 + 200, h * 0.62 + 400], outline="#8EB8FF", width=4)
    img.save(out, "PNG")
    return out


def ensure_brand_assets() -> tuple[Path, Path]:
    return generate_profile_image(), generate_banner_image()
