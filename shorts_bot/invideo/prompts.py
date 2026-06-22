"""InVideo creative briefs — Shorts-native framing (not long-form stock)."""

from __future__ import annotations

# InVideo defaults to long-form stock crops unless we spell out vertical rules.
SHORTS_VISUAL_RULES = """
FORMAT: YouTube Short ONLY — 9:16 vertical, 25-35 seconds. NOT long-form. NOT 16:9.

VISUAL MIX (owner rule — stock-first, twin is accent):
- Use LICENSED STOCK FOOTAGE for most of the runtime — aim for 70–85% stock B-roll
- AI twin (AlphaBeta Host): SHORT inserts only — hook (1–3s), verdict (2–4s), maybe one mid beat; never long talking-head stretches
- Voiceover carries the review; visuals = stock + product UI, not twin on camera the whole time
- Pick stock that fits tech/AI/productivity themes (phones, laptops, typing, thinking, money, decision moments) — vertical-safe, center-weighted
- NO horizontal stock squeezed into vertical with ugly letterboxing — choose vertical-native stock or tight center crops
- Also use tight app UI / screen recordings where the product matters
- Max 5–6 visual beats — fast cuts, no slow Ken Burns pans
- Captions: bold bottom third, Shorts safe zone (keep clear of YouTube UI overlay)
- Hook: brief twin OR bold text + stock in first 2 seconds
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
        "Presenter: Ms. Byte (saved library character RTR_MsByte) — anime/cel-shaded bubbly AI teacher, ~5s on screen; stock + app UI otherwise. NO AI twin.",
        "YOU write the script — this is the creative brief only, not a finished script.",
    ]
    if extra.strip():
        parts.append(extra.strip())
    return "\n".join(parts)


DEFAULT_CHATGPT_PLUS_BRIEF = shorts_product_brief(
    product="ChatGPT Plus",
    hook="Is the $20/month actually worth it for normal people?",
    verdict_hint="Pay, Skip, or Wait",
    extra="Stock-heavy edit: licensed B-roll for most shots; twin only 1–3 sec hook + 2–4 sec verdict. ChatGPT UI where needed — vertical crops.",
)
