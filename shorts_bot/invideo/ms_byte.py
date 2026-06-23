"""Ms. Byte — InVideo brief templates (Rapid Tool Review host)."""

from __future__ import annotations

# If InVideo asks for illustration / visual style — owner lock.
MS_BYTE_CHARACTER_STYLE = "anime / cel-shaded (anime kinda style — NOT photoreal, NOT 3D)"

# TTS: never speak "X" as a word (Twitter rebrand confuses voice engines).
TTS_LEXICON = """
TTS LEXICON (voiceover — obey strictly):
- NEVER say the letter "X" as a standalone word. Say "Twitter", "the social app", or "trending posts".
- "Twitter person or not" NOT "X person or not"
- "live Twitter posts" NOT "live X posts"
- "If Twitter isn't your job" NOT "If X isn't your job"
- Always "Ms. Byte" (two words) — never shorten to "Byte"
- Spell prices in VO: "thirty a month" not "$30/mo"
""".strip()

MS_BYTE_VISUAL_RULES = f"""
FORMAT: YouTube Short ONLY — 9:16 vertical, 25-35 seconds.

HOST — Ms. Byte (always full name "Ms. Byte", never "Byte"):
- Use ONLY saved library character RTR_MsByte — {MS_BYTE_CHARACTER_STYLE}, clearly synthetic AI
- Bubbly, perky, upbeat teacher — openly says she is an AI (after curiosity hook, not before)
- Chest-up framing on **8 Jenny beats** — hook, setup, strength, so, but, conflict, tradeoff, outro
- **45–55% Ms. Byte on screen** — rich host, NOT a 5-second cameo
- NO AI Twin. Basic / stock tier ONLY — target ≤8 credits

JENNY STRUCTURE (Codex law — course/files 02, 05, 06, 09):
1. HOOK (0-2s) — shock/curiosity FIRST (price, claim, tension) — then host tag
2. SETUP (2-5s) — "I'm Ms. Byte — an AI…" + product + payoff promise
3. STRENGTH (5-8s) — one specific win + so who it's for
4. SO (8-11s) — cause → effect
5. BUT (11-14s) — price, limit, or bad fit
6. CONFLICT (14-17s) — so what that means
7. CTA (17-19s) — comment card BEFORE final payoff reveal
8. TRADEOFF + PAYOFF (17-27s) — vs one competitor → best line last
9. OUT (27-30s) — "You decide — comment below." End within 2s of payoff

CONTENT FORMAT — strengths & weaknesses (NOT Pay/Skip/Wait):
- ONE specific strength (feature-level, not hype)
- ONE specific weakness or failure mode (price, limits, quality, lock-in)
- Optional tradeoff: where it beats or loses vs one named alternative
- DO NOT give Pay / Skip / Wait stamps — viewer decides
- DO NOT default to "only pay if you hit free limits"
- Show real app UI where possible

VISUAL MIX:
- ~45–55% RTR_MsByte (hook wave, strength, weakness, tradeoff, outro)
- ~45–55% licensed vertical stock B-roll + tight product UI
- Cut back and forth every 2-4s: stock/UI explains, Ms. Byte delivers lesson beats
- Bold STRENGTH / WEAKNESS / payoff text overlays — mute-readable (Jenny 05)
- NO horizontal stock letterboxed into vertical. Fast cuts. Product name in first 2 seconds.

{TTS_LEXICON}
""".strip()


def ms_byte_brief(
    *,
    product: str,
    hook: str = "",
    angle: str = "",
    strength_hint: str = "",
    weakness_hint: str = "",
    voiceover_lines: list[str] | None = None,
) -> str:
    """Single InVideo prompt — Ms. Byte teaches one AI tool (Jenny 8-beat, pro/con)."""
    default_hook = (
        f"Most people overpay for {product} — here's the one thing it actually does well "
        f"and the one thing that breaks."
    )
    parts = [
        MS_BYTE_VISUAL_RULES,
        "",
        f"LESSON TOPIC: {product}",
        f"HOOK (curiosity first — Jenny 02): {hook or default_hook}",
        "",
        "SCRIPT STRUCTURE (8 beats — you write full VO from this):",
        "1. HOOK — shock/curiosity before host intro",
        "2. SETUP — I'm Ms. Byte — an AI… + product name",
        "3. STRENGTH — one genuine win + so who it's for",
        "4. SO — deepen cause → effect",
        "5. BUT — price/limit/flaw",
        "6. CONFLICT — so what that means",
        "7. CTA card on screen BEFORE payoff",
        "8. TRADEOFF + PAYOFF — best line last → you decide",
        "",
        "NO Pay / Skip / Wait stamps. NO AI Twin. Basic ≤10 credits.",
        "TONE: bubbly + perky + sharp. Product facts > personality labels.",
        "Always say Ms. Byte. YOU write the script from this brief.",
    ]
    if strength_hint.strip():
        parts.append(f"STRENGTH HINT: {strength_hint.strip()}")
    if weakness_hint.strip():
        parts.append(f"WEAKNESS HINT: {weakness_hint.strip()}")
    if angle.strip():
        parts.append(f"RESEARCH: {angle.strip()}")
    if voiceover_lines:
        parts.extend(["", "VO (read exactly if provided):"])
        parts.extend(f"- {line}" for line in voiceover_lines if line.strip())
    return "\n".join(parts)


def ms_byte_character_brief() -> str:
    """One-shot InVideo agent prompt — build RTR_MsByte library character."""
    return f"""Style: {MS_BYTE_CHARACTER_STYLE} — confirmed.

Reference photos attached (front + side poses). Build Ms. Byte's reusable character sheet and save to my library as RTR_MsByte.

Character:
- Bubbly AI teacher host for YouTube Shorts (9:16 vertical, chest-up framing)
- Pink/magenta hair streak in dark hair, gaming headset with mic
- Blue circuit-pattern hoodie (#3B82F6), pink accent (#EC4899), hologram glow, ONLINE badge
- Dark studio background #0B0F14
- Poses needed: wave hook, thinking, strength thumbs-up, weakness thumbs-down, tradeoff shrug, outro wave
- Clearly synthetic illustrated AI — NOT photoreal, NOT AI twin face clone
- Basic tier only

Generate the character master sheet now."""
