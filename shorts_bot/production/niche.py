"""Niche — AI / Tech Shorts (channel rebrand)."""

from __future__ import annotations

NICHE_NAME = "AI Tech Shorts"
NICHE_TAGLINE = "Honest AI in 30 seconds."

NICHE_POSITIONING = """
**AI / Tech Shorts** — ~30 second explainers with a **clear takeaway** (verdict, myth bust, or one workflow).
Presenter: owner **InVideo AI twin** (consistent face + voice). Stock UI / tech B-roll. Captions on.

Target hierarchy (lock sub-sub with owner):
- Big: **AI / Tech**
- Sub: **AI tools for normal people** OR **AI literacy**
- Sub-sub: **Honest tool verdicts** OR **one scary truth about AI per Short**

Format rules:
- Hook in line 1 = **claim or question** (not vague mood)
- One topic only — one tool OR one myth OR one workflow
- End with **verdict or takeaway** (Pay / Skip / Wait — or "remember this")
- 25–35s; captions burned in InVideo
- Original opinion every time — not Wikipedia summary

What works: skeptical honesty, specific limitation, save-worthy myth, your face on camera.
What fails: prompt spam lists, hype thumbnails, horror tone, template farms, "make $10k" energy.
"""

DEFAULT_TOPICS = [
    "I paid for ChatGPT Pro so you don't have to — here's when to skip it",
    "that AI headshot app hides this in the fine print",
    "voice clones need three seconds of audio — not thirty minutes",
    "NotebookLM is free and useful — one catch nobody mentions",
    "AI essay detectors are mostly guessing — don't trust the score",
    "InVideo vs CapCut AI — honest thirty second pick for Shorts",
    "your ChatGPT history isn't private — read this before you paste secrets",
    "this AI girlfriend app is worse than the ads show",
    "why AI still can't count reliably — ten second proof",
    "the free tier sells your data — how to spot it on any AI site",
    "I tried an AI meeting notetaker for a week — skip if you do this",
    "Gemini vs ChatGPT for research — one clear winner for most people",
    "that viral AI video tool watermark — what you actually get on free",
    "don't upload your kid's photos to that AI app — here's why",
    "AI resume builders — one actually helped, two wasted an hour",
    "the 'AI detected' label on social media is mostly theater",
    "I automated my captions with AI — workflow in thirty seconds",
    "OpenAI o-series hype vs what normal users actually need",
    "this browser extension reads everything you type — AI privacy check",
    "Sora-style video AI — wait before you pay, here's why",
]


def quality_lessons() -> str:
    return (
        "Better: specific tool or myth, honest verdict, one clear limitation, twin presenter, "
        "readable captions, hook in first line. "
        "Worse: generic prompt lists, hype without testing, horror tone, finance spam, "
        "multiple topics in one Short. "
        "Always: declare synthetic presenter when required, 1 Short per 24h, original script."
    )
