"""Ms. Byte Facebook status posts — picture + on-image text + alive caption."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shorts_bot.brand.assets import (
    ACCENT,
    ACCENT_BRIGHT,
    BG_TOP,
    MS_BYTE_DIR,
    TEXT_MUTED,
    TEXT_PRIMARY,
    _extract_character_rgba,
    _font_for_width,
    _hex_rgb,
    _solid_background,
)

OUTPUT_DIR = Path("data/social/status_posts")

# pose file, headline (on image), subline (on image), Facebook caption (first-person Ms. Byte)
STATUS_TEMPLATES: tuple[tuple[str, str, str, str], ...] = (
    (
        "pose_hook_surprise.png",
        "New lesson dropping soon.",
        "Grok · $30 · live Twitter data",
        "Okay okay — Grok breakdown lands on YouTube Tuesday at 8am. "
        "I'm Ms. Byte (yes, an AI) and I actually read the pricing page so you don't have to. "
        "Which tool next? 👇 #RapidToolReview #MsByte #Grok",
    ),
    (
        "pose_teach_pointing.png",
        "Class is in session.",
        "One strength · one weakness · you decide",
        "I'm not grading you — I'm grading the tool. "
        "Rapid Tool Review = honest 30-second AI breakdowns with zero hype-bro energy. "
        "Follow if you want the receipts, not the marketing page. ✨ #AITools #MsByte",
    ),
    (
        "pose_thinking.png",
        "Still awake?",
        "Good. Let's talk AI subscriptions.",
        "It's 11pm and I'm literally code — but Grok at thirty a month vs ChatGPT at twenty "
        "is the kind of drama I live for. New Short soon. You decide if it's worth it. 💭",
    ),
    (
        "pose_cta_comment.png",
        "Pick my next lesson.",
        "Comment a tool name below",
        "ChatGPT? Claude? Cursor? NotebookLM? "
        "Tell me what to break down next — I'll pick the spiciest comment. "
        "(Kindly. With facts. I'm a teacher, not a troll.) 👇 #RapidToolReview",
    ),
    (
        "pose_payoff.png",
        "Yes I'm synthetic.",
        "No I won't fake being human.",
        "Light British voice, bubbly energy, clearly AI — that's the whole bit. "
        "Ms. Byte runs this channel about other AI tools. "
        "If that confuses the algorithm, good. We're still learning together. 💅 #MsByte",
    ),
)


@dataclass
class StatusPostAsset:
    slug: str
    image_path: Path
    caption: str


def _wrap_headline(draw, text: str, font, max_width: int, max_lines: int = 3) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join(current + [word])
        w = draw.textlength(trial, font=font) if hasattr(draw, "textlength") else len(trial) * 14
        if w <= max_width or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(" ".join(current))
    return lines[:max_lines]


def generate_status_post_image(
    *,
    pose_file: str,
    headline: str,
    subline: str,
    out_path: Path,
    size: int = 1080,
) -> Path:
    """Square feed post — Ms. Byte + text panel (status-update vibe)."""
    from PIL import Image, ImageDraw

    img = _solid_background(size, size, BG_TOP)
    draw = ImageDraw.Draw(img)

    # Accent bar top
    draw.rectangle([0, 0, size, 8], fill=_hex_rgb(ACCENT_BRIGHT))
    draw.rectangle([0, 8, size, 14], fill=_hex_rgb("#EC4899"))

    pose_path = MS_BYTE_DIR / pose_file
    if not pose_path.exists():
        pose_path = MS_BYTE_DIR / "reference_916_front.png"
    host = _extract_character_rgba(pose_path)
    target_h = int(size * 0.62)
    scale = target_h / host.height
    host = host.resize((int(host.width * scale), target_h), Image.Resampling.LANCZOS)
    host_x = 24
    host_y = size - host.height - 20
    img.paste(host, (host_x, host_y), host)

    panel_x = int(size * 0.38)
    panel_y = int(size * 0.12)
    panel_w = size - panel_x - 36
    panel_h = int(size * 0.42)
    draw.rounded_rectangle(
        [panel_x, panel_y, panel_x + panel_w, panel_y + panel_h],
        radius=20,
        fill=(18, 24, 32),
        outline=_hex_rgb(ACCENT),
        width=2,
    )

    badge_font = _font_for_width(draw, "Ms. Byte", max_width=panel_w - 40, start_size=22, min_size=16)
    draw.text((panel_x + 24, panel_y + 18), "Ms. Byte", fill=_hex_rgb(ACCENT_BRIGHT), font=badge_font)
    draw.ellipse([panel_x + panel_w - 52, panel_y + 22, panel_x + panel_w - 36, panel_y + 38], fill=(34, 197, 94))
    online_font = _font_for_width(draw, "ONLINE", max_width=80, start_size=14, min_size=12)
    draw.text((panel_x + panel_w - 88, panel_y + 20), "ONLINE", fill=_hex_rgb(TEXT_MUTED), font=online_font)

    text_max_w = panel_w - 48
    head_font = _font_for_width(draw, headline, max_width=text_max_w, start_size=44, min_size=28)
    lines = _wrap_headline(draw, headline, head_font, text_max_w)
    y = panel_y + 56
    for line in lines:
        draw.text((panel_x + 24, y), line, fill=_hex_rgb(TEXT_PRIMARY), font=head_font)
        y += int(getattr(head_font, "size", 36) * 1.15)

    sub_font = _font_for_width(draw, subline, max_width=text_max_w, start_size=26, min_size=18, bold=False)
    draw.text((panel_x + 24, panel_y + panel_h - 52), subline, fill=_hex_rgb(TEXT_MUTED), font=sub_font)

    handle_font = _font_for_width(draw, "@RapidToolReview", max_width=text_max_w, start_size=20, min_size=14, bold=False)
    draw.text((panel_x + 24, size - 48), "@RapidToolReview", fill=_hex_rgb(ACCENT), font=handle_font)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    return out_path


def _slugify(text: str) -> str:
    import re

    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:48] or "status"


def build_status_posts(*, limit: int | None = None) -> list[StatusPostAsset]:
    templates = STATUS_TEMPLATES[:limit] if limit else STATUS_TEMPLATES
    out: list[StatusPostAsset] = []
    for pose, headline, subline, caption in templates:
        slug = _slugify(headline)
        path = OUTPUT_DIR / f"{slug}.png"
        generate_status_post_image(pose_file=pose, headline=headline, subline=subline, out_path=path)
        out.append(StatusPostAsset(slug=slug, image_path=path, caption=caption))
    return out


def post_image_to_facebook(image_path: Path, caption: str) -> dict:
    """Upload one status image to Facebook Page via Zernio."""
    import httpx

    from shorts_bot.zernio.client import _request, account_id_for, credentials_configured

    if not credentials_configured():
        raise RuntimeError("ZERNIO_API_KEY not configured")
    fb_id = account_id_for("facebook")
    if not fb_id:
        raise RuntimeError("No Facebook account on Zernio")

    body = _request(
        "POST",
        "/media/presign",
        json={
            "filename": image_path.name,
            "contentType": "image/png",
            "size": image_path.stat().st_size,
        },
    )
    raw = image_path.read_bytes()
    with httpx.Client(timeout=120) as client:
        resp = client.put(
            body["uploadUrl"],
            content=raw,
            headers={"Content-Type": "image/png", "Content-Length": str(len(raw))},
        )
    if resp.status_code not in (200, 201, 204):
        raise RuntimeError(f"Zernio media upload failed ({resp.status_code})")

    payload = {
        "content": caption[:2200],
        "mediaItems": [{"type": "image", "url": body["publicUrl"]}],
        "platforms": [{"platform": "facebook", "accountId": fb_id}],
        "publishNow": True,
    }
    resp = _request("POST", "/posts", json=payload)
    post = resp.get("post") or resp
    url = ""
    for p in post.get("platforms") or []:
        if (p.get("platform") or "").lower() == "facebook":
            url = p.get("platformPostUrl") or ""
    return {
        "post_id": str(post.get("_id") or post.get("id") or ""),
        "status": str(post.get("status") or ""),
        "url": url,
    }
