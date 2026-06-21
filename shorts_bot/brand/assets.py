"""Generate channel profile + banner PNGs — Rapid Tool Review brand."""

from __future__ import annotations

from pathlib import Path

ASSETS_DIR = Path("channel/brand/assets")
PROFILE_PATH = ASSETS_DIR / "profile.png"
BANNER_PATH = ASSETS_DIR / "banner.png"

# channel/brand/visual_identity.md
BG_TOP = "#0B0F14"
BG_MID = "#121820"
ACCENT = "#3B82F6"
ACCENT_BRIGHT = "#60A5FA"
TEXT_PRIMARY = "#F8FAFC"
TEXT_MUTED = "#94A3B8"
PAY = "#22C55E"
SKIP = "#EF4444"
WAIT = "#F59E0B"


def _load_fonts(size_lg: int, size_md: int, size_sm: int, *, mono_lg: int = 0):
    from PIL import ImageFont

    candidates_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    candidates_reg = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    candidates_mono = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
    ]
    font_lg = font_md = font_sm = font_mono = ImageFont.load_default()
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
    if mono_lg:
        for path in candidates_mono:
            try:
                font_mono = ImageFont.truetype(path, mono_lg)
                break
            except OSError:
                continue
    return font_lg, font_md, font_sm, font_mono


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


def _draw_verdict_pills(draw, cx: int, y: int, font, *, gap: int = 28) -> None:
    labels = [("PAY", PAY), ("SKIP", SKIP), ("WAIT", WAIT)]
    widths = []
    pad_x, pad_y = 18, 8
    for label, _ in labels:
        w = draw.textlength(label, font=font) if hasattr(draw, "textlength") else 60
        widths.append(w + pad_x * 2)
    total = sum(widths) + gap * (len(labels) - 1)
    x = cx - total // 2
    for (label, color), bw in zip(labels, widths, strict=True):
        bh = 44
        draw.rounded_rectangle([x, y, x + bw, y + bh], radius=10, fill=color)
        tw = draw.textlength(label, font=font) if hasattr(draw, "textlength") else 40
        draw.text((x + (bw - tw) / 2, y + pad_y - 2), label, fill=TEXT_PRIMARY, font=font)
        x += bw + gap


def generate_profile_image(out_path: Path | None = None) -> Path:
    """800×800 profile — RTR monogram, readable at avatar size."""
    from PIL import Image, ImageDraw

    out = out_path or PROFILE_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    size = 800
    img = Image.new("RGB", (size, size), BG_TOP)
    _vertical_gradient(img, BG_TOP, BG_MID)
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    for r, color, width in ((340, ACCENT, 4), (300, ACCENT_BRIGHT, 2)):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)

    _, _, _, font_mono = _load_fonts(28, 24, 20, mono_lg=168)
    mark = "RTR"
    tw = draw.textlength(mark, font=font_mono) if hasattr(draw, "textlength") else 200
    draw.text((cx - tw / 2, cy - 90), mark, fill=TEXT_PRIMARY, font=font_mono)

    _, font_md, font_sm, _ = _load_fonts(28, 34, 22)
    sub = "30 sec"
    sw = draw.textlength(sub, font=font_sm) if hasattr(draw, "textlength") else 80
    draw.text((cx - sw / 2, cy + 40), sub, fill=TEXT_MUTED, font=font_sm)

    _draw_verdict_pills(draw, cx, cy + 110, font_md)

    img.save(out, "PNG", optimize=True)
    return out


def generate_banner_image(out_path: Path | None = None) -> Path:
    """2560×1440 banner — Rapid Tool Review, YouTube safe-zone centered."""
    from PIL import Image, ImageDraw

    out = out_path or BANNER_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    w, h = 2560, 1440
    img = Image.new("RGB", (w, h), BG_TOP)
    _vertical_gradient(img, BG_TOP, "#0F172A")
    draw = ImageDraw.Draw(img)

    cx = w // 2
    font_lg, font_md, font_sm, font_mono = _load_fonts(118, 52, 38, mono_lg=44)

    eyebrow = "AI TOOL REVIEWS"
    ew = draw.textlength(eyebrow, font=font_sm) if hasattr(draw, "textlength") else 400
    draw.text(((w - ew) / 2, h * 0.28), eyebrow, fill=ACCENT_BRIGHT, font=font_sm)

    title = "Rapid Tool Review"
    tw = draw.textlength(title, font=font_lg) if hasattr(draw, "textlength") else 1400
    draw.text(((w - tw) / 2, h * 0.36), title, fill=TEXT_PRIMARY, font=font_lg)

    sub = "Honest AI tools · Fast verdicts · ~30 seconds"
    sw = draw.textlength(sub, font=font_md) if hasattr(draw, "textlength") else 1100
    draw.text(((w - sw) / 2, h * 0.50), sub, fill=ACCENT, font=font_md)

    _draw_verdict_pills(draw, cx, int(h * 0.58), font_sm, gap=36)

    handle = "@RapidToolReview"
    hw = draw.textlength(handle, font=font_mono) if hasattr(draw, "textlength") else 500
    draw.text(((w - hw) / 2, h * 0.68), handle, fill=TEXT_MUTED, font=font_mono)

    img.save(out, "PNG", optimize=True)
    return out


def ensure_brand_assets(*, force: bool = False) -> tuple[Path, Path]:
    """Return Rapid Tool Review assets; regenerate when missing or force=True."""
    if not force and PROFILE_PATH.exists() and BANNER_PATH.exists():
        return PROFILE_PATH, BANNER_PATH
    return generate_profile_image(), generate_banner_image()
