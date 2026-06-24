"""Niche — Rapid Tool Review RETIRED (2026-06-24). See archive/rapid_tool_review/."""

from __future__ import annotations

from shorts_bot.production.rtr_retired import ARCHIVE_ROOT, RETIRED_LABEL

# Active placeholder until owner locks next sub-niche
NICHE_NAME = "AI / Tech"
NICHE_TAGLINE = "AI explains tech — one clear takeaway per Short."

NICHE_POSITIONING = """
**AI / Tech Shorts** — ~30 second YouTube Shorts on real tools, products, or workflows.

**Rapid Tool Review is RETIRED** (2026-06-24) — same as Peripheral horror. Full RTR kit archived under `archive/rapid_tool_review/`. Do not use RTR branding, @RapidToolReview, Pay/Skip/Wait series framing, or Ms. Byte host specs for new work unless owner revives them.

Hierarchy (placeholder until owner reassesses):
- Big: **AI / Tech**
- Sub: **TBD** — owner picks next locked sub-niche
- Format: **Conversational** — one clear takeaway; no Pay/Skip/Wait stamps; no AI twin

Production:
- InVideo one-prompt ship, Basic tier ≤10 credits, NO AI Twin
- Conversational tool-teaching format (see `shorts_bot/invideo/invideo_master_prompt.md`)

Tone: honest, direct, no hype. Real product names when reviewing tools.
What fails: retired RTR/Ms. Byte branding, Pay/Skip/Wait stamps, horror framing, twin talking heads.
"""

DEFAULT_TOPICS = [
    "ChatGPT Plus — what the paid tier actually unlocks",
    "Claude Code — terminal agent honest breakdown",
    "InVideo AI — credit math for daily Shorts",
    "NotebookLM — free tool hidden limits",
    "Gemini Advanced — paid vs free Gemini",
    "Cursor Pro — inline AI editor breakdown",
    "Perplexity Pro — search tier comparison",
    "Grok xAI — live feed vs chat bots",
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
        "Better: strong hook in first 2s, one named product or topic, specific takeaway, "
        "mute-readable overlays, conversational close. "
        "Worse: retired Rapid Tool Review branding, Pay/Skip/Wait stamps, Ms. Byte host spec, "
        "vague AI hype, multi-product listicles, horror/jumpscare framing. "
        "Always: synthetic disclosure, 1 Short/24h YPP-safe."
    )


def retired_rtr_note() -> str:
    return f"{RETIRED_LABEL} archived at {ARCHIVE_ROOT}/ — reference only."
