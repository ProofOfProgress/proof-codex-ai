"""Niche — Fix It Fast · TikTok Shop gadget Shorts (locked 2026-06-24)."""

from __future__ import annotations

NICHE_NAME = "Fix It Fast"
NICHE_TAGLINE = "Problem solved in seconds."

NICHE_POSITIONING = """
**Fix It Fast** — TikTok Shop Shorts selling **home, kitchen, and car problem-solver gadgets** (~$15–$35 impulse buys).

**Primary platform:** TikTok Shop (orange cart / shopping bag). YouTube repost optional for extra views.

**Not our lane:** AI software reviews, affiliates, Rapid Tool Review (retired → `archive/rapid_tool_review/`), Ms. Byte, Pay/Skip/Wait.

**Format (every Short):**
1. HOOK — show the problem in 2 seconds (mess, stuck lid, dark closet)
2. DEMO — hands + product fix it (satisfying before/after)
3. PAYOFF — one simple benefit line
4. CTA — "Linked in the orange cart" / "Tap the shopping bag"

**Production:** InVideo one-prompt, Basic ≤10 credits, NO AI Twin, NO mascot. Product is the star.

**Business model:** Product-hop constantly — test many SKUs, kill losers, scale winners. Supplier/dropship via TikTok Shop catalog.

Tone: upbeat, visual, satisfying — not medical claims, not listicles, not software UI reviews.
What fails: AI tool walkthroughs, horror, Ms. Byte, twin talking heads, fake miracle claims.
"""

DEFAULT_TOPICS = [
    "Car Seat Gap Filler — stops stuff falling between seats",
    "Jar Grip Opener — pops stuck lids in seconds",
    "Magnetic Cable Clips — desk cable mess fix",
    "Motion Sensor LED Strip — dark closet fix",
    "Mini Car Vacuum — crumbled chips and dust gone fast",
    "Sink Drain Hair Catcher — shower clog prevention",
    "Car Sunshade Umbrella — hot steering wheel fix",
    "Vegetable Chopper — dice onions without crying",
]

SHOP_RULES = """
TikTok Shop rules:
- ONE physical product per Short — pin Shop product link when listing exists
- Honest demo — show real use case, no fake before/after
- Disclose #ad if TikTok marks as sponsored
- Kill products that don't convert after fair test volume; hop to next SKU
"""


def quality_lessons() -> str:
    return (
        "Better: problem visible in first 2s, hands/product demo, satisfying fix, clear Shop CTA, "
        "mute-readable text overlays, 15-30s tight. "
        "Worse: AI tool UI reviews, Ms. Byte/RTR branding, listicles, no product on screen, "
        "slow 5s intros, horror framing, medical miracle claims. "
        "Always: 1 product per Short, synthetic disclosure when applicable."
    )
