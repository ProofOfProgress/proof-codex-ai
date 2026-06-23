"""Generate channel profile + banner PNGs — Rapid Tool Review brand."""

from __future__ import annotations

import math
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


def _draw_ai_review_mark(draw, cx: int, cy: int, *, scale: float = 1.0) -> None:
    """Universal AI signal: magnifying glass over a 3-node network (not one brand)."""
    s = scale
    lens_r = int(118 * s)
    lens_cx, lens_cy = cx, cy - int(18 * s)

    # Soft outer glow rings
    for r_off, color, width in (
        (int(24 * s), "#1E3A5F", int(10 * s)),
        (int(12 * s), ACCENT, int(4 * s)),
    ):
        r = lens_r + r_off
        draw.ellipse(
            [lens_cx - r, lens_cy - r, lens_cx + r, lens_cy + r],
            outline=color,
            width=max(1, width),
        )

    # Lens fill + ring
    draw.ellipse(
        [lens_cx - lens_r, lens_cy - lens_r, lens_cx + lens_r, lens_cy + lens_r],
        fill=_hex_rgb(BG_MID),
        outline=_hex_rgb(ACCENT_BRIGHT),
        width=max(2, int(10 * s)),
    )

    # Neural nodes inside lens (triangle layout)
    node_r = max(2, int(14 * s))
    nodes = [
        (lens_cx, lens_cy - int(42 * s)),
        (lens_cx - int(52 * s), lens_cy + int(34 * s)),
        (lens_cx + int(52 * s), lens_cy + int(34 * s)),
    ]
    for i, j in ((0, 1), (0, 2), (1, 2)):
        draw.line([nodes[i], nodes[j]], fill=_hex_rgb(ACCENT), width=max(2, int(6 * s)))
    for nx, ny in nodes:
        draw.ellipse(
            [nx - node_r, ny - node_r, nx + node_r, ny + node_r],
            fill=_hex_rgb(TEXT_PRIMARY),
            outline=_hex_rgb(ACCENT_BRIGHT),
            width=max(1, int(3 * s)),
        )

    # Handle — bottom-right from lens
    angle = math.radians(38)
    hx0 = lens_cx + int(lens_r * 0.62 * math.cos(angle))
    hy0 = lens_cy + int(lens_r * 0.62 * math.sin(angle))
    hx1 = hx0 + int(92 * s)
    hy1 = hy0 + int(92 * s)
    draw.line(
        [(hx0, hy0), (hx1, hy1)],
        fill=_hex_rgb(ACCENT_BRIGHT),
        width=max(3, int(18 * s)),
    )
    cap = max(2, int(10 * s))
    draw.ellipse(
        [hx1 - cap, hy1 - cap, hx1 + cap, hy1 + cap],
        fill=_hex_rgb(ACCENT_BRIGHT),
    )


def generate_profile_image(out_path: Path | None = None) -> Path:
    """800×800 profile — AI magnifier mark, readable at YouTube avatar size."""
    from PIL import Image, ImageDraw

    out = out_path or PROFILE_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    size = 800
    img = Image.new("RGB", (size, size), BG_TOP)
    _vertical_gradient(img, BG_TOP, BG_MID)
    draw = ImageDraw.Draw(img)
    _draw_ai_review_mark(draw, size // 2, size // 2 + 20, scale=1.0)
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


MS_BYTE_DIR = Path("channel/brand/assets/ms_byte")
MS_BYTE_PROFILE = MS_BYTE_DIR / "social_profile.png"
MS_BYTE_FB_COVER = MS_BYTE_DIR / "facebook_cover.png"
MS_BYTE_TT_COVER = MS_BYTE_DIR / "tiktok_cover.png"


def _crop_ms_byte_profile(source: Path, out: Path, *, size: int = 800) -> Path:
    """Square avatar — chest-up, face centered (reads at small sizes)."""
    from PIL import Image

    img = Image.open(source).convert("RGBA")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = max(0, int(h * 0.02))
    side = min(side, h - top)
    cropped = img.crop((left, top, left + side, top + side))
    cropped = cropped.resize((size, size), Image.Resampling.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    cropped.convert("RGB").save(out, "PNG", optimize=True)
    return out


def generate_ms_byte_facebook_cover(out_path: Path | None = None) -> Path:
    """1640×624 Facebook cover — Ms. Byte + Rapid Tool Review (mobile-safe center)."""
    from PIL import Image, ImageDraw

    out = out_path or MS_BYTE_FB_COVER
    w, h = 1640, 624
    img = Image.new("RGB", (w, h), BG_TOP)
    _vertical_gradient(img, BG_TOP, "#0F172A")
    draw = ImageDraw.Draw(img)

    host_path = MS_BYTE_DIR / "pose_hook_wave.png"
    if not host_path.exists():
        host_path = MS_BYTE_DIR / "reference.png"
    host = Image.open(host_path).convert("RGBA")
    target_h = int(h * 1.15)
    scale = target_h / host.height
    host = host.resize((int(host.width * scale), target_h), Image.Resampling.LANCZOS)
    img.paste(host, (-int(host.width * 0.08), h - target_h + 20), host)

    font_lg, font_md, font_sm, font_mono = _load_fonts(72, 36, 28, mono_lg=30)
    cx = int(w * 0.58)
    draw.text((cx, int(h * 0.22)), "Rapid Tool Review", fill=TEXT_PRIMARY, font=font_lg)
    draw.text((cx, int(h * 0.48)), "Ms. Byte · AI tool reviews", fill=ACCENT_BRIGHT, font=font_md)
    draw.text((cx, int(h * 0.62)), "Strengths · Weaknesses · You decide", fill=TEXT_MUTED, font=font_sm)
    draw.text((cx, int(h * 0.76)), "@RapidToolReview on YouTube", fill=ACCENT, font=font_mono)

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return out


def generate_ms_byte_tiktok_cover(out_path: Path | None = None) -> Path:
    """TikTok header-style 1120×660 — Ms. Byte + channel name."""
    from PIL import Image, ImageDraw

    out = out_path or MS_BYTE_TT_COVER
    w, h = 1120, 660
    img = Image.new("RGB", (w, h), BG_TOP)
    _vertical_gradient(img, BG_TOP, "#0F172A")
    draw = ImageDraw.Draw(img)

    host_path = MS_BYTE_DIR / "reference.png"
    host = Image.open(host_path).convert("RGBA")
    target_h = int(h * 1.1)
    scale = target_h / host.height
    host = host.resize((int(host.width * scale), target_h), Image.Resampling.LANCZOS)
    img.paste(host, (-int(host.width * 0.05), h - target_h + 10), host)

    font_lg, font_md, font_sm, _ = _load_fonts(64, 34, 26)
    cx = int(w * 0.55)
    draw.text((cx, int(h * 0.28)), "Rapid Tool Review", fill=TEXT_PRIMARY, font=font_lg)
    draw.text((cx, int(h * 0.50)), "Ms. Byte — AI reviewing AI tools", fill=ACCENT_BRIGHT, font=font_md)
    draw.text((cx, int(h * 0.66)), "Honest breakdowns · You decide", fill=TEXT_MUTED, font=font_sm)

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return out


def ensure_ms_byte_social_assets(*, force: bool = False) -> dict[str, Path]:
    """Profile + Facebook/TikTok cover art featuring Ms. Byte."""
    ref = MS_BYTE_DIR / "reference.png"
    if not ref.exists():
        raise FileNotFoundError(f"Missing {ref} — run InVideo character CLI or unzip ms_byte assets")

    if force or not MS_BYTE_PROFILE.exists():
        _crop_ms_byte_profile(ref, MS_BYTE_PROFILE)
    if force or not MS_BYTE_FB_COVER.exists():
        generate_ms_byte_facebook_cover()
    if force or not MS_BYTE_TT_COVER.exists():
        generate_ms_byte_tiktok_cover()

    return {
        "profile": MS_BYTE_PROFILE,
        "facebook_cover": MS_BYTE_FB_COVER,
        "tiktok_cover": MS_BYTE_TT_COVER,
    }
