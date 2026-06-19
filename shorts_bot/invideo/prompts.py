"""InVideo creative briefs — Shorts-native framing (not long-form stock)."""

from __future__ import annotations

# InVideo defaults to long-form stock crops unless we spell out vertical rules.
SHORTS_VISUAL_RULES = """
FORMAT: YouTube Short ONLY — 9:16 vertical, 25-35 seconds. NOT long-form. NOT 16:9.

VISUAL RULES (critical — previous run had wonky widescreen stock crops):
- Every shot must be composed for VERTICAL mobile — subject centered, no wide cinematic letterboxing
- NO horizontal stock footage cropped into vertical — looks broken
- Prefer: fullscreen talking-head (AI twin), tight mobile phone UI screenshots, single-product close-ups
- Max 4-5 visual beats total — fast cuts, no slow Ken Burns pans
- B-roll: screen recordings and app UI only; skip generic office/laptop stock unless tightly center-cropped
- Captions: bold bottom third, Shorts safe zone (keep clear of YouTube UI overlay)
- Hook in first 2 seconds on camera or bold text
""".strip()


def shorts_product_brief(
    *,
    product: str,
    hook: str,
    verdict_hint: str = "Pay, Skip, or Wait",
    extra: str = "",
) -> str:
    """Creative brief for InVideo — it writes the script; we specify Shorts framing."""
    parts = [
        SHORTS_VISUAL_RULES,
        "",
        f"TOPIC: {product} — honest 30-second review for normal people.",
        f"HOOK: {hook}",
        f"CLOSE: clear {verdict_hint} verdict + one sentence why.",
        "TONE: skeptical but fair — not hype, not affiliate energy.",
        "Presenter: use MY saved AI Twin avatar (not stock actors). Twin on camera fullscreen for most shots.",
        "YOU write the script — this is the creative brief only, not a finished script.",
    ]
    if extra.strip():
        parts.append(extra.strip())
    return "\n".join(parts)


DEFAULT_CHATGPT_PLUS_BRIEF = shorts_product_brief(
    product="ChatGPT Plus",
    hook="Is the $20/month actually worth it for normal people?",
    verdict_hint="Pay, Skip, or Wait",
    extra="Show ChatGPT mobile/desktop UI — tight crops, not wide desk stock shots.",
)
