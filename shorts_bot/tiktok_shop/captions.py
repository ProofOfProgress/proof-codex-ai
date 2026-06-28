"""Sale-style captions — no discount percentages (2026 Shop policy)."""

from __future__ import annotations

import re

BANNED_IN_CAPTION = re.compile(
    r"\d+\s*%\s*off|\d+\s*percent|\b\d{1,2}%\b|half\s+off|BOGO",
    re.I,
)

# Owner on-screen burn-in template (VIDEO_EDITOR.md) — copy changes often; update there first.
ON_SCREEN_CAPTION_TEMPLATE = (
    "I am SO sorry if you already grabbed {product} because the discount is huge today"
)

CAPTION_TEMPLATES = (
    "{product} is on a crazy deal right now — free shipping too",
    "Hurry — {product} stock is running low on TikTok Shop",
    "If you need {product}, grab it before this sale ends",
    "{product} is violently discounted today with free shipping",
    "Last chance vibe — {product} won't stay this cheap long",
    "Everyone's grabbing {product} on Shop — sale ends soon",
    "Don't sleep on {product} — deal + free shipping today",
    "Your cart will thank you — {product} is basically a steal rn",
    "Still need {product}? TikTok Shop has it on sale today",
    "Quick heads up — {product} is moving fast at this price",
)


def format_product_title(name: str) -> str:
    """Title-case each word for on-screen captions (e.g. pre workout powder → Pre Workout Powder)."""
    return " ".join(part[:1].upper() + part[1:] if part else part for part in name.split())


def on_screen_caption(product_name: str) -> str:
    """Owner default on-screen hook — see VIDEO_EDITOR.md."""
    product = format_product_title((product_name or "this").strip()) or "This"
    return ON_SCREEN_CAPTION_TEMPLATE.format(product=product)


def sanitize_caption(text: str) -> str:
    cleaned = BANNED_IN_CAPTION.sub("sale", text)
    return cleaned.strip()[:2200]


def caption_variants(product_name: str, *, limit: int = 10) -> list[str]:
    name = (product_name or "this").strip() or "this"
    out: list[str] = []
    for tpl in CAPTION_TEMPLATES:
        cap = sanitize_caption(tpl.format(product=name))
        if cap and cap not in out:
            out.append(cap)
        if len(out) >= limit:
            break
    return out
