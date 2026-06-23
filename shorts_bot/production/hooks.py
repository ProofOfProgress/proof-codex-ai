"""Jenny-compliant hooks for Rapid Tool Review — templates, scoring, migration."""

from __future__ import annotations

import re

# Patterns that produce scroll-past hooks — script_qc uses these.
WEAK_HOOK_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bis .+ worth it\b", re.I), "Generic 'is X worth it' — use price shock or contrarian claim"),
    (re.compile(r"\bworth it\?", re.I), "Weak 'worth it?' — lead with price, flaw, or 'most shouldn't pay'"),
    (re.compile(r"\bi tested if", re.I), "'I tested if' — viewer doesn't care about your test, lead with tension"),
    (re.compile(r"\beveryone'?s paying for", re.I), "Cliché opener — be specific (price, limit, surprise)"),
    (re.compile(r"\b30.?second verdict", re.I), "Meta framing — hook should BE the verdict tension"),
    (re.compile(r"\bif you'?re thinking about", re.I), "Slow warm-up — start with shock, not consideration"),
    (re.compile(r"\bhonest 30s take", re.I), "Template slop — show the tension, not 'honest take'"),
    (re.compile(r"\bhere'?s my honest", re.I), "Warm-up filler — curiosity or price first"),
    (re.compile(r"\bpay or skip", re.I), "Pay/Skip/Wait retired — use strength/weakness tension"),
    (re.compile(r"\bclass is in session", re.I), "Host intro before hook — Jenny 02 violation"),
    (re.compile(r"\bhey guys\b", re.I), "Filler intro"),
)

# Jenny-compliant rotation pool — used when queue hook missing.
HOOK_TEMPLATES: tuple[str, ...] = (
    "{product} costs money — and most casual users shouldn't pay.",
    "Stop ignoring this about {product} — one strength, one flaw, thirty seconds.",
    "{product} looks perfect on the landing page — here's what breaks.",
    "Most people overpay for {product} — here's the one thing it actually does well.",
    "{product} — the price is real, the hype isn't. Quick breakdown.",
)

# Curated hooks per product (fallback when template would be generic).
PRODUCT_HOOKS: dict[str, str] = {
    "chatgpt plus": "Twenty bucks for ChatGPT Plus — and most casual users shouldn't pay.",
    "claude code": "Claude Code sounds amazing — but most people should not pay for this.",
    "claude pro": "Twenty bucks for Claude — but ChatGPT already covers most writers.",
    "google gemini advanced": "Google wants twenty for Gemini Advanced — free Gemini might be enough.",
    "invideo ai": "InVideo can ship a Short in minutes — but the credit math catches people.",
    "cursor pro": "Cursor Pro looks perfect — unless you don't write code daily.",
    "perplexity pro": "Ten bucks for Perplexity Pro — but free search got scary good.",
    "notebooklm": "NotebookLM is free — here's the one reason people still skip it.",
    "capcut ai": "CapCut AI is bundled free — until you need export without a watermark.",
    "elevenlabs": "ElevenLabs voice clones sound human — until you check the price meter.",
    "heygen": "HeyGen's AI avatars look real — InVideo does Shorts for half the burn.",
    "midjourney": "Midjourney still wins on art — but the subscription stack adds up fast.",
    "notion ai": "Notion AI sits inside your notes — but the add-on price adds up.",
    "descript": "Descript edits podcasts like magic — overkill if you only make Shorts.",
    "runway gen-3": "Runway looks amazing — but the credit burn adds up fast.",
    "opus clip": "Opus Clip chops long videos into Shorts — if the AI picks wrong, you're sunk.",
    "grok (xai)": "Thirty bucks for Grok — and most of you shouldn't pay.",
}


def hook_for_product(product: str, *, template_index: int = 0) -> str:
    """Best hook for a product name — curated first, then template."""
    key = product.strip().lower()
    if key in PRODUCT_HOOKS:
        return PRODUCT_HOOKS[key]
    tpl = HOOK_TEMPLATES[template_index % len(HOOK_TEMPLATES)]
    return tpl.format(product=product)


def score_hook(hook: str) -> tuple[float, list[str]]:
    """Return (score 0-10, issues). 10 = strong Jenny hook."""
    issues: list[str] = []
    score = 10.0
    text = hook.strip()
    if not text:
        return 0.0, ["Empty hook"]
    words = len(text.split())
    if words > 18:
        issues.append("Hook too long (>18 words)")
        score -= 2.0
    if words < 6:
        issues.append("Hook too short — add price, claim, or tension")
        score -= 2.0
    for pattern, msg in WEAK_HOOK_PATTERNS:
        if pattern.search(text):
            issues.append(msg)
            score -= 2.5
    # Reward Jenny signals
    lower = text.lower()
    if any(w in lower for w in ("shouldn't pay", "should not pay", "most people", "most casual", "most of you")):
        score += 0.5
    if re.search(r"\$\d+|twenty|thirty|ten bucks|free —", lower):
        score += 0.5
    if "but" in lower or "until" in lower or "—" in text:
        score += 0.25
    return max(0.0, min(10.0, score)), issues


def migrate_verdict_hint(verdict_hint: str) -> tuple[str, str]:
    """Legacy queue verdict_hint → (strength_hint, weakness_hint)."""
    v = (verdict_hint or "").strip()
    if not v:
        return "", ""
    if re.search(r"\bSkip\b", v, re.I):
        cleaned = re.sub(r"\bSkip\b\s*", "", v, flags=re.I).strip(" ;—-:")
        return "", cleaned or v
    if re.search(r"\bWait\b", v, re.I):
        cleaned = re.sub(r"\bWait\b\s*", "", v, flags=re.I).strip(" ;—-:")
        return "", cleaned or v
    if re.search(r"\bPay\b", v, re.I):
        cleaned = re.sub(r"\bPay\b\s*(if|unless)?\s*", "", v, flags=re.I).strip(" ;—-:")
        return cleaned or v, ""
    return "", v
