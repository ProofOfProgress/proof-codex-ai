"""Ms. Byte — InVideo brief templates (Rapid Tool Review host)."""

from __future__ import annotations

MS_BYTE_VISUAL_RULES = """
FORMAT: YouTube Short ONLY — 9:16 vertical, 25-35 seconds.

HOST — Ms. Byte (always full name "Ms. Byte", never "Byte"):
- Use ONLY saved library character RTR_MsByte — flat 2D cartoon, clearly synthetic AI
- Bubbly, perky, upbeat teacher — openly says she is an AI in the hook
- Chest-up framing ~5 seconds total (hook + pro/con beat); rest = stock + tight app UI
- NO AI Twin. Basic / stock tier ONLY — target ≤8 credits

CONTENT FORMAT — strengths & weaknesses (NOT Pay/Skip/Wait):
- ONE specific strength of this product (feature-level, not hype)
- ONE specific weakness or failure mode (price, limits, quality, lock-in)
- Optional tradeoff: where it beats or loses vs one named alternative
- DO NOT give a definitive "worth it / not worth it" for the viewer — they decide
- DO NOT default to "only pay if you hit free limits" — say what's unique about THIS tool
- Show real app UI where possible

VISUAL MIX: 70–85% vertical stock + product UI. Fast cuts. Bold captions. Product name in first 2 seconds.
""".strip()


def ms_byte_brief(
    *,
    product: str,
    hook: str = "",
    angle: str = "",
    strength_hint: str = "",
    weakness_hint: str = "",
) -> str:
    """Single InVideo prompt — Ms. Byte teaches one AI tool (pro/con, not verdict)."""
    default_hook = (
        f"Class is in session! Hi — I'm Ms. Byte! Yes, I'm an AI! "
        f"Today's lesson: {product} — what's actually good and what's actually broken!"
    )
    parts = [
        MS_BYTE_VISUAL_RULES,
        "",
        f"LESSON TOPIC: {product}",
        f"HOOK (perky): {hook or default_hook}",
        "",
        "SCRIPT STRUCTURE:",
        "1. STRENGTH — one thing this product genuinely does well (specific)",
        "2. WEAKNESS — one real flaw, limit, or bad fit (specific)",
        "3. TRADEOFF — optional: vs one competitor on one axis — not a buy command",
        "4. CLOSE — perky: 'That's the lesson — you decide! Comment your use case!'",
        "",
        "NO Pay / Skip / Wait stamps. NO universal 'don't pay unless you hit limits'.",
        "TONE: bubbly + perky + sharp. Product facts > personality labels.",
        "Always say Ms. Byte. YOU write the script from this brief.",
    ]
    if strength_hint.strip():
        parts.append(f"STRENGTH HINT: {strength_hint.strip()}")
    if weakness_hint.strip():
        parts.append(f"WEAKNESS HINT: {weakness_hint.strip()}")
    if angle.strip():
        parts.append(f"RESEARCH: {angle.strip()}")
    return "\n".join(parts)
