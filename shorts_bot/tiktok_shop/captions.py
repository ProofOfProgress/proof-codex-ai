"""Sale-style captions — no discount percentages (2026 Shop policy)."""

from __future__ import annotations

import re
from pathlib import Path

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


def wrap_hook_lines(
    text: str,
    *,
    max_chars_per_line: int | None = None,
    max_lines: int | None = None,
) -> list[str]:
    """
    Break hook copy into lines for TikTok native text or burn-in.
    Owner rule: **never exceed 18 characters per line** (config default — safe margin on TikTok).
    """
    from shorts_bot.config import settings

    limit = max_chars_per_line if max_chars_per_line is not None else settings.tiktok_shop_caption_max_chars_per_line
    line_cap = max_lines if max_lines is not None else settings.tiktok_shop_caption_max_lines
    limit = max(1, int(limit))
    line_cap = max(1, int(line_cap))

    clean = " ".join((text or "").split())
    if not clean:
        return []

    lines: list[str] = []
    current: list[str] = []

    def flush() -> None:
        nonlocal current
        if current:
            lines.append(" ".join(current))
            current = []

    for word in clean.split():
        if len(word) > limit:
            flush()
            for i in range(0, len(word), limit):
                lines.append(word[i : i + limit])
            continue
        trial = " ".join([*current, word]) if current else word
        if len(trial) <= limit:
            current.append(word)
        else:
            flush()
            current = [word]
    flush()

    if len(lines) > line_cap:
        lines = lines[:line_cap]
        last = lines[-1]
        if len(last) >= limit:
            lines[-1] = last[: limit - 1] + "…"
        else:
            lines[-1] = last + "…"

    return [ln for ln in lines if ln]


def wrap_hook_text(text: str, **kwargs: object) -> str:
    """Newline-joined hook lines (TikTok paste / ffmpeg textfile)."""
    return "\n".join(wrap_hook_lines(text, **kwargs))


def hook_sidecar_path(video_path: Path) -> Path:
    """`.hook.txt` next to clip — one line per row for TikTok native text."""
    return Path(video_path).with_suffix(".hook.txt")


def save_hook_sidecar(video_path: Path, text: str) -> Path:
    path = hook_sidecar_path(video_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    wrapped = wrap_hook_text(text)
    path.write_text(wrapped + ("\n" if wrapped else ""), encoding="utf-8")
    return path


def validate_hook_lines(lines: list[str], *, max_chars: int | None = None) -> list[str]:
    """Return lines that exceed the per-line character limit."""
    from shorts_bot.config import settings

    limit = max_chars if max_chars is not None else settings.tiktok_shop_caption_max_chars_per_line
    return [ln for ln in lines if len(ln) > limit]


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
