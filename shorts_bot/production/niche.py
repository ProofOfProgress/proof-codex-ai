"""Niche — AI product tech reviews (locked 2026-06)."""

from __future__ import annotations

NICHE_NAME = "AI Product Reviews"
NICHE_TAGLINE = "Honest AI in 30 seconds."

NICHE_POSITIONING = """
**AI Product Reviews** — ~30 second Shorts reviewing **real AI products** with a clear verdict.
Presenter: owner **InVideo AI twin**. Product UI / tech B-roll. Captions on.

Hierarchy (locked):
- Big: **AI / Tech**
- Sub: **AI product reviews**
- Sub-sub: **Honest verdict on one real product** — Pay / Skip / Wait

Format:
- Hook line 1: claim about the product ("Everyone's paying for X — I tested it.")
- Body: one genuine flaw, surprise, or strength — not a feature dump
- Close: **Pay / Skip / Wait** + one sentence why
- 25–35s; one named product per Short

Tone: **sincere honesty first** — praise when earned, skip when deserved. No hype voice.
Future: sponsors/affiliates allowed only with disclosure; sponsored scripts need owner approval; never fake "I tested it."

What works: real product names, specific price/privacy/quality callouts, twin on camera, clear verdict.
What fails: prompt lists, undisclosed ads, generic AI news, fake testing, finance spam, template farms.
"""

DEFAULT_TOPICS = [
    "ChatGPT Plus — honest thirty second verdict",
    "InVideo AI — worth it for Shorts creators",
    "that AI headshot app — skip it if you care about privacy",
    "NotebookLM vs ChatGPT for research — one clear winner",
    "CapCut AI vs InVideo — I tested both for Shorts",
    "this AI meeting notetaker — pay or skip",
    "Gemini Advanced — who actually needs it",
    "ChatGPT vs Claude for writing — honest pick",
    "that viral AI video tool — what the free tier actually gives you",
    "AI resume builder I tried for an hour — verdict",
    "Perplexity Pro — pay or stay on free",
    "HeyGen vs InVideo for AI avatar Shorts",
    "Notion AI — worth adding to your workspace",
    "Adobe Firefly vs Midjourney for beginners",
    "this AI voice clone app — the privacy catch",
    "Cursor Pro for non-coders — honest take",
    "Descript AI editing — skip if you only make Shorts",
    "ElevenLabs voice clone — pay tier or free enough",
    "Synthesia vs InVideo — talking head Shorts compared",
    "the new OpenAI feature — wait before you pay",
]

SPONSOR_RULES = """
Sponsor / affiliate rules (future):
- Disclose paid partnerships in video and description (#ad).
- Organic reviews and sponsored content use separate queues.
- Sponsored scripts require owner approval; no automatic Pay verdict.
- Affiliate links only for products we'd honestly recommend; disclose commission.
"""


def quality_lessons() -> str:
    return (
        "Better: named real product, tested claim, one sharp pro/con, Pay/Skip/Wait verdict, "
        "twin presenter, readable captions. "
        "Worse: vague 'AI tool', hype without substance, undisclosed sponsor praise, "
        "multi-product listicles, prompt spam. "
        "Always: sincere honesty, 1 product per Short, synthetic presenter disclosure, 1 Short/24h."
    )
