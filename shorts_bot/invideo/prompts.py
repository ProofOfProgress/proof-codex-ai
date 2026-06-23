"""InVideo creative briefs — delegates to Ms. Byte Jenny format."""

from __future__ import annotations

from shorts_bot.invideo.ms_byte import MS_BYTE_VISUAL_RULES, ms_byte_brief

# Legacy alias — daily workflow and tests import from here.
SHORTS_VISUAL_RULES = MS_BYTE_VISUAL_RULES


def shorts_product_brief(
    *,
    product: str,
    hook: str,
    verdict_hint: str = "",
    extra: str = "",
    strength_hint: str = "",
    weakness_hint: str = "",
) -> str:
    """Creative brief for InVideo — Ms. Byte strength/weakness format (Jenny 8-beat)."""
    angle = extra.strip()
    if verdict_hint.strip() and not strength_hint and not weakness_hint:
        angle = f"{angle}\nResearch note: {verdict_hint.strip()}".strip()
    return ms_byte_brief(
        product=product,
        hook=hook,
        angle=angle,
        strength_hint=strength_hint,
        weakness_hint=weakness_hint,
    )


DEFAULT_CHATGPT_PLUS_BRIEF = shorts_product_brief(
    product="ChatGPT Plus",
    hook="ChatGPT Plus costs twenty a month — here's what the paid tier unlocks.",
    strength_hint="Strong writing, voice, and plugins for daily power users.",
    weakness_hint="$20/month adds little over free tier for light chat — same model family on both.",
    extra="Tradeoff vs Gemini free tier for research-heavy workflows.",
)
