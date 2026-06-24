"""Jenny-compliant hooks for Fix It Fast TikTok Shop gadget Shorts."""

from __future__ import annotations

import re

# Patterns that produce scroll-past hooks — script_qc uses these.
WEAK_HOOK_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bis .+ worth it\b", re.I), "Generic 'is X worth it' — show the problem first"),
    (re.compile(r"\bworth it\?", re.I), "Weak 'worth it?' — lead with the annoyance"),
    (re.compile(r"\bi tested if", re.I), "'I tested if' — show the problem visually first"),
    (re.compile(r"\beveryone'?s buying", re.I), "Vague social proof — name the specific problem"),
    (re.compile(r"\b\d+\s+(gadgets|tools|hacks|products)", re.I), "Listicle — one product per Short"),
    (re.compile(r"\bhey guys\b", re.I), "Filler intro"),
    (re.compile(r"\byou won'?t believe", re.I), "Clickbait warm-up — show problem in frame 1"),
)

HOOK_TEMPLATES: tuple[str, ...] = (
    "{product} fixes this annoying problem in seconds — watch.",
    "Stop dealing with this — {product} handles it in one move.",
    "This {product} looks simple — but it saves ten minutes every day.",
    "Why is nobody using {product} for this mess?",
    "{product} — problem gone in three seconds.",
)

PRODUCT_HOOKS: dict[str, str] = {
    "car seat gap filler": "Stuff keeps falling between your car seats — this gap filler catches everything.",
    "jar grip opener": "Jar lid won't budge? This grip tool pops it open in three seconds.",
    "magnetic cable clips": "Desk cables look like this? These magnetic clips clean it up in ten seconds.",
    "motion sensor led strip": "Why is your closet pitch black every morning? This motion LED fixes it.",
    "mini car vacuum": "Crushed chips in the car seat? This mini vacuum pulls it out in seconds.",
    "sink drain hair catcher": "Shower drain clogging again? This catcher stops hair before it sinks.",
    "car sunshade umbrella": "Steering wheel too hot to touch? This fold umbrella shade blocks it.",
    "vegetable chopper": "Dicing onions takes forever — this chopper does it in one press.",
}


def hook_for_product(product: str, *, template_index: int = 0) -> str:
    """Best hook for a product name — curated first, then template."""
    key = product.strip().lower()
    if key in PRODUCT_HOOKS:
        return PRODUCT_HOOKS[key]
    tpl = HOOK_TEMPLATES[template_index % len(HOOK_TEMPLATES)]
    return tpl.format(product=product)


def score_hook(hook: str) -> tuple[float, list[str]]:
    """Return (score 0-10, issues). 10 = strong problem-first hook."""
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
        issues.append("Hook too short — add problem or product tension")
        score -= 2.0
    for pattern, msg in WEAK_HOOK_PATTERNS:
        if pattern.search(text):
            issues.append(msg)
            score -= 3.5 if "listicle" in msg.lower() else 2.5
    lower = text.lower()
    if any(w in lower for w in ("won't", "stuck", "falls", "falling", "mess", "dark", "clog", "hot", "chips", "forever")):
        score += 0.5
    if "?" in text or "—" in text or "this" in lower:
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
