"""TikTok Shop gadget briefs — Fix It Fast (problem → demo → cart CTA)."""

from __future__ import annotations

SHOP_VISUAL_RULES = """
FORMAT: TikTok / YouTube Short — 9:16 vertical ONLY, 15-30 seconds (max 35).

BRAND: Fix It Fast — home, kitchen, and car problem-solver gadgets (impulse buys under ~$35).

PRESENTER: NO AI Twin. NO cartoon mascot. NO Ms. Byte. Product is the star.
- Hands + product on screen (POV or tabletop demo)
- Licensed vertical stock OK when product clip unavailable
- Satisfying before/after — problem visible, then fix

STRUCTURE (every video):
1. HOOK (0-2s) — show the annoying PROBLEM first (mess, stuck jar, dark closet, fallen phone)
2. DEMO (2-18s) — product fixes it; tight cuts; hands using the gadget; satisfying result
3. PAYOFF (18-24s) — one line why it works (simple, not tech-bro)
4. SHOP CTA (24-28s) — "Linked in the orange cart" / "Tap the shopping bag" / "Shop tag below"

VISUAL MIX:
- ~70% product in use (hands, close-ups, satisfying reveal)
- ~30% bold text overlays — PROBLEM → FIXED — mute-readable
- Fast cuts every 2-4s. NO horizontal letterboxing. NO talking-head filler.

VOICE: US English, female or neutral, upbeat, fast clear pacing for Shorts. Conversational seller energy — not hype scream, not corporate.

DO NOT:
- Software UI walkthroughs, app reviews, Pay/Skip/Wait stamps
- Ms. Byte, AI Twin, RTR branding (retired)
- "5 gadgets you need" listicles — ONE product per Short
- Fake claims ("cures arthritis", medical guarantees)
- Horror, jumpscares, AI tool review framing
""".strip()


def shop_brief(
    *,
    product: str,
    hook: str = "",
    angle: str = "",
    strength_hint: str = "",
    weakness_hint: str = "",
    verdict_hint: str = "",
    voiceover_lines: list[str] | None = None,
) -> str:
    """Single InVideo prompt — TikTok Shop gadget demo (problem → fix → cart)."""
    problem = weakness_hint.strip() or "Show a relatable everyday annoyance this product solves."
    demo = strength_hint.strip() or "Show the product working — satisfying before/after."
    cta = verdict_hint.strip() or "Linked in the orange cart — tap the shopping bag."

    default_hook = f"This {product} fixes an annoying problem in seconds — watch."
    parts = [
        SHOP_VISUAL_RULES,
        "",
        f"PRODUCT: {product}",
        f"HOOK (problem first): {hook or default_hook}",
        "",
        "SCRIPT STRUCTURE:",
        "1. HOOK — visual problem in first 2 seconds",
        "2. DEMO — hands/product fix it",
        "3. PAYOFF — one simple benefit line",
        "4. SHOP CTA — orange cart / shopping bag",
        "",
        f"PROBLEM TO SHOW: {problem}",
        f"DEMO / SATISFYING MOMENT: {demo}",
        f"SHOP CTA LINE: {cta}",
        "NO AI Twin. Basic tier ≤10 credits. YOU write the script from this brief.",
    ]
    if angle.strip():
        parts.append(f"NOTES: {angle.strip()}")
    if voiceover_lines:
        parts.extend(["", "VO (read exactly if provided):"])
        parts.extend(f"- {line}" for line in voiceover_lines if line.strip())
    return "\n".join(parts)
