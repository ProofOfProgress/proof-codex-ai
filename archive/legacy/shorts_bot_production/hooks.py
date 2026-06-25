"""Jenny-compliant hooks for Rapid Tool Review — templates, scoring, migration."""

from __future__ import annotations

import re

# Patterns that produce scroll-past hooks — script_qc uses these.
WEAK_HOOK_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bis .+ worth it\b", re.I), "Generic 'is X worth it' — use price shock or tool fact"),
    (re.compile(r"\bworth it\?", re.I), "Weak 'worth it?' — lead with price, feature, or what breaks"),
    (re.compile(r"\bi tested if", re.I), "'I tested if' — viewer doesn't care about your test, lead with tension"),
    (re.compile(r"\beveryone'?s paying for", re.I), "Cliché opener — be specific (price, limit, surprise)"),
    (re.compile(r"\b30.?second verdict", re.I), "Meta framing — hook should BE the tension"),
    (re.compile(r"\bif you'?re thinking about", re.I), "Slow warm-up — start with shock, not consideration"),
    (re.compile(r"\bhonest 30s take", re.I), "Template slop — show the tension, not 'honest take'"),
    (re.compile(r"\bhere'?s my honest", re.I), "Warm-up filler — curiosity or price first"),
    (re.compile(r"\bpay or skip", re.I), "Pay/Skip/Wait retired — use strength/weakness tension"),
    (re.compile(r"\bclass is in session", re.I), "Host intro before hook — Jenny 02 violation"),
    (re.compile(r"\bhey guys\b", re.I), "Filler intro"),
    # Audience-verdict framing — teach the tool, not who should buy
    (re.compile(r"\bshouldn'?t pay\b", re.I), "Audience verdict — teach what the tool does / breaks instead"),
    (re.compile(r"\bshould not pay\b", re.I), "Audience verdict — teach tool facts instead"),
    (re.compile(r"\bwho (it'?s|should|actually needs)", re.I), "Who-it's-for framing — teach the tool instead"),
    (re.compile(r"\bunless you don'?t\b", re.I), "Audience filter — name the tool flaw instead"),
    (re.compile(r"\bmost casual users\b", re.I), "Audience filter — name price or limit instead"),
    (re.compile(r"\bmost of you\b", re.I), "Audience filter — name the product fact instead"),
)

# Jenny-compliant rotation pool — tool facts, not buyer advice.
HOOK_TEMPLATES: tuple[str, ...] = (
    "{product} has a price tag — here's what the paid tier actually unlocks.",
    "Stop ignoring this about {product} — one strength, one flaw, thirty seconds.",
    "{product} looks perfect on the landing page — here's what breaks.",
    "Most people misunderstand {product} — here's the one thing it actually does well.",
    "{product} — the price is real, the hype isn't. Quick breakdown.",
)

# Curated hooks per product (fallback when template would be generic).
PRODUCT_HOOKS: dict[str, str] = {
    "chatgpt plus": "ChatGPT Plus costs twenty a month — here's what the paid tier unlocks.",
    "claude code": "Claude Code runs in your terminal — and it burns through Pro limits fast.",
    "claude pro": "Claude Pro is twenty a month — here's where it beats ChatGPT on writing.",
    "google gemini advanced": "Gemini Advanced bundles two terabytes — the AI upgrade isn't always the win.",
    "invideo ai": "InVideo can ship a Short in minutes — but the credit math catches people.",
    "cursor pro": "Cursor Pro rewrites your whole codebase inline — the subscription adds up fast.",
    "perplexity pro": "Perplexity Pro adds cited research mode — free search already got scary good.",
    "notebooklm": "NotebookLM reads your PDFs and cites them back — it just can't browse the web.",
    "capcut ai": "CapCut AI is bundled free — until you need export without a watermark.",
    "elevenlabs": "ElevenLabs voice clones sound human — until you check the price meter.",
    "heygen": "HeyGen's AI avatars look real — InVideo does Shorts for half the burn.",
    "midjourney": "Midjourney still wins on art — but the subscription stack adds up fast.",
    "notion ai": "Notion AI sits inside your notes — but the add-on price adds up.",
    "descript": "Descript edits video by deleting words from the transcript — the subscription is steep.",
    "runway gen-3": "Runway looks amazing — but the credit burn adds up fast.",
    "opus clip": "Opus Clip chops long videos into Shorts — if the AI picks wrong, you're sunk.",
    "grok (xai)": "Grok costs thirty a month — it's built around live Twitter data.",
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
    # Reward tool-teaching signals (not audience verdicts)
    lower = text.lower()
    if any(w in lower for w in ("unlocks", "built for", "built around", "breaks", "burns", "catch")):
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
