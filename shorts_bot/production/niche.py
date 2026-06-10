"""Niche v2 — The Minute Before (Soft Continuity)."""

from __future__ import annotations

NICHE_NAME = "The Minute Before"
NICHE_TAGLINE = "one moment. one fix."

NICHE_POSITIONING = """
Soft Continuity — niche v2: **The Minute Before**

One specific high-stakes moment → one concrete 60-second protocol.
Not generic "sleep tips" or hustle motivation. Faceless stick-figure visuals + first-person voice.

Pillars (rotate):
1. **Conversations** — before hard talks, angry replies, apologies
2. **Work threshold** — before email, meetings, Sunday dread
3. **Body alarm** — chest tight, can't sleep, Sunday scaries (only when moment-specific)
4. **Social edge** — parties, boundaries, saying no in one sentence
5. **After the slip** — shame spiral, replaying, procrastination guilt

What worked (draft 7): specific moment, stick figures acting each beat, personal arc, 8 paced beats.
What underperformed (early drafts): vague topics ("sleep"), too few beats, generic hooks.
"""

DEFAULT_TOPICS = [
    "the minute before a hard conversation",
    "the minute before you send an angry text",
    "the minute before you open work email on Sunday",
    "the minute before a presentation",
    "the minute before you walk into a party alone",
    "the minute before you say yes when you mean no",
    "the minute before a difficult apology",
    "the minute before you doom-scroll in bed",
    "the minute before a job interview",
    "the minute before you snap at someone you love",
    "the minute before a doctor appointment",
    "the minute before you check your bank account",
    "the minute before a family dinner",
    "the minute before you quit scrolling and try to sleep",
    "the minute before you bring up money",
    "the minute before a first date",
    "the minute before you log off work",
    "the minute before a performance review",
    "the minute before you set a boundary with a friend",
    "the minute before you open a message you're dreading",
    "the minute before a tough workout when you want to skip",
    "the minute before you cry in the bathroom at work",
    "the minute before you compare yourself online",
    "the minute before a commute when dread hits",
    "the minute before you procrastinate again",
    "the minute before you rehearse a breakup talk",
    "the minute before you wake up already anxious",
    "the minute before you cancel plans from guilt",
    "the minute before you ask for help",
    "the minute before you forgive yourself for today",
]


def quality_lessons() -> str:
    return (
        "Better: draft 7 — 'minute before hard conversation', stick figure scenes, 8 segments, "
        "first-person arc, specific stakes. "
        "Worse: early 'sleep' drafts — vague topic, 4 segments, generic hook 'Stop scrolling'. "
        "Always: hook in first line, mute-safe captions in Jenny 05 safe zone (above Shorts UI)."
    )
