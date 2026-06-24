"""InVideo creative briefs — TikTok Shop gadget demos (Fix It Fast)."""

from __future__ import annotations

from shorts_bot.invideo.shop_brief import SHOP_VISUAL_RULES, shop_brief

# Legacy alias — daily workflow and tests import from here.
SHORTS_VISUAL_RULES = SHOP_VISUAL_RULES


def shorts_product_brief(
    *,
    product: str,
    hook: str,
    verdict_hint: str = "",
    extra: str = "",
    strength_hint: str = "",
    weakness_hint: str = "",
) -> str:
    """Creative brief for InVideo — TikTok Shop problem → demo → cart."""
    angle = extra.strip()
    if verdict_hint.strip() and not strength_hint and not weakness_hint:
        angle = f"{angle}\nShop note: {verdict_hint.strip()}".strip()
    return shop_brief(
        product=product,
        hook=hook,
        angle=angle,
        strength_hint=strength_hint,
        weakness_hint=weakness_hint,
        verdict_hint=verdict_hint,
    )


DEFAULT_SHOP_BRIEF = shorts_product_brief(
    product="Car Seat Gap Filler",
    hook="Stuff keeps falling between your car seats — this gap filler catches everything.",
    weakness_hint="Phone, keys, and fries disappear into the seat crack every drive.",
    strength_hint="Flexible insert fills the gap — stuff sits on top instead of vanishing.",
    verdict_hint="Linked in the orange cart — tap the shopping bag.",
)
