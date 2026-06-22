"""Ms. Byte — InVideo brief templates (Rapid Tool Review host)."""

from __future__ import annotations

MS_BYTE_VISUAL_RULES = """
FORMAT: YouTube Short ONLY — 9:16 vertical, 25-35 seconds.

HOST — Ms. Byte (always full name "Ms. Byte", never "Byte"):
- Use ONLY saved library character RTR_MsByte — flat 2D cartoon, clearly synthetic AI (hologram glow, ONLINE badge, UI accents)
- Bubbly, perky, upbeat teacher energy — warm and fast, not deadpan
- She openly says she is an AI in the hook — not pretending to be human
- Chest-up framing ~5 seconds total (hook + verdict); rest = licensed stock + tight app UI
- Stylized cartoon outfit; face and teaching beat stay the focus
- NO AI Twin. NO photoreal presenter. Basic / stock tier ONLY — target ≤8 credits

VISUAL MIX:
- 70–85% vertical stock B-roll + product UI / screen recordings
- Max 5–6 beats — fast cuts
- Bold captions, bottom third, Shorts safe zone
- Product name large on screen in first 2 seconds
""".strip()


def ms_byte_brief(
    *,
    product: str,
    hook: str = "",
    angle: str = "",
    verdict_hint: str = "Pay, Skip, Wait, or name a better alternative",
) -> str:
    """Single InVideo prompt — Ms. Byte teaches one AI tool."""
    default_hook = (
        f"Class is in session! Hi — I'm Ms. Byte! Yes, I'm an AI! "
        f"Today's lesson: {product} — is it actually worth your money?"
    )
    parts = [
        MS_BYTE_VISUAL_RULES,
        "",
        f"LESSON TOPIC: {product} — teach one AI tool in ~30 seconds.",
        f"HOOK (perky, first line): {hook or default_hook}",
        "",
        "TEACH: price, who it's for, one honest flaw or surprise. Show real app UI.",
        f"VERDICT: {verdict_hint} — one clear sentence. Can say a BETTER tool by name if Skip.",
        "CLOSE: perky sign-off — next lesson tomorrow.",
        "",
        "TONE: bubbly + perky + sharp. Funny contrast: cute AI teacher, brutal honesty about bad tools.",
        "Always address her as Ms. Byte in script. YOU write the script from this brief.",
    ]
    if angle.strip():
        parts.extend(["", f"RESEARCH: {angle.strip()}"])
    return "\n".join(parts)
