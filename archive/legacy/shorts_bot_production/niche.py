"""Niche — Rapid Tool Review / Ms. Byte (locked 2026-06)."""

from __future__ import annotations

NICHE_NAME = "Rapid Tool Review"
NICHE_TAGLINE = "An AI explains AI tools — strengths, weaknesses, you decide."

NICHE_POSITIONING = """
**Rapid Tool Review** (@RapidToolReview) — ~30 second YouTube Shorts reviewing **one real AI product**.
Host: **Ms. Byte** — saved InVideo library character `RTR_MsByte`, clearly synthetic AI teacher.

Hierarchy (locked):
- Big: **AI / Tech**
- Sub: **Honest AI tool reviews for normal people**
- Format: **One strength + one weakness** — viewer decides (NO Pay/Skip/Wait stamps)

Jenny Codex (course/files 02, 05, 06, 09):
- Hook = price shock or contrarian claim in first 2 seconds — NOT "is X worth it?"
- 8 beats, 2–4s cuts, CTA before payoff, mute-readable overlays
- Cause → effect: strength → so (feature depth) → but → so (cost of flaw) → tradeoff → payoff

Production:
- InVideo MCP one-prompt ship, Basic tier ≤10 credits, NO AI Twin
- Ms. Byte ~45–55% on screen; rest = vertical stock + product UI

Tone: bubbly teacher + skeptical honesty. No hype, no affiliate energy, no fake testing.
What works: real product names, specific price/limit callouts, Jenny hooks, app UI on screen.
What fails: generic "worth it" hooks, Pay/Skip/Wait stamps, listicles, horror framing, twin talking heads.
"""

DEFAULT_TOPICS = [
    "ChatGPT Plus — twenty bucks, what the paid tier unlocks",
    "Claude Code — terminal agent honest breakdown",
    "InVideo AI — credit math for daily Shorts",
    "NotebookLM — free tool hidden limits",
    "Gemini Advanced — twenty vs free Gemini",
    "Cursor Pro — inline AI editor breakdown",
    "Perplexity Pro — ten bucks vs free search",
    "CapCut AI — watermark trap on export",
    "ElevenLabs — voice clone credit burn",
    "HeyGen vs InVideo — avatar Shorts cost",
    "Midjourney — subscription stack in 2026",
    "Notion AI — add-on tax on workspace",
    "Descript — transcript-edit workflow cost",
    "Runway Gen-3 — credit burn per clip",
    "Opus Clip — AI clip picks wrong moments",
    "Grok xAI — thirty bucks for live Twitter data",
]

SPONSOR_RULES = """
Sponsor / affiliate rules (future):
- Disclose paid partnerships in video and description (#ad).
- Organic reviews and sponsored content use separate queues.
- Sponsored scripts require owner approval.
- Affiliate links only for products we'd honestly recommend; disclose commission.
"""


def quality_lessons() -> str:
    return (
        "Better: Jenny hook (price/contrarian first), one named product, specific strength + weakness, "
        "Ms. Byte host, mute-readable overlays, you decide close. "
        "Worse: 'Is X worth it?', 'I tested if', Pay/Skip/Wait stamps, vague AI hype, "
        "multi-product listicles, horror/jumpscare framing. "
        "Always: 1 product per Short, synthetic disclosure, 1 Short/24h YPP-safe."
    )
