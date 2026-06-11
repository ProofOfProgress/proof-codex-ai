"""YouTube inauthentic-content / spam-farm counter-rules (2025–2026 policy).

Sources: YouTube channel monetization policies (repetitious → inauthentic, Jul 2025),
spam & deceptive practices sweeps on mass-produced AI slideshow farms.

YouTube does NOT ban AI tools — it targets mass-produced template output with no editorial value.
"""

from __future__ import annotations

import re

# Patterns that signal spam-farm / inauthentic content
TITLE_SPAM_PATTERNS = [
    re.compile(r"^[A-Z\s!?0-9]{12,}$"),  # ALL CAPS shock titles
    re.compile(r"you won'?t believe", re.I),
    re.compile(r"gone wrong|instant regret|watch till the end", re.I),
    re.compile(r"#shorts\s*#shorts", re.I),
]

SCRIPT_FARM_PHRASES = [
    "in today's fast-paced world",
    "game changer",
    "let's dive in",
    "without further ado",
    "unlock your potential",
    "the ultimate guide",
    "here's the thing you need to know",
    "subscribe for more",
    "smash that like button",
    "comment below which",
    "number one will shock you",
]

FIRST_PERSON = re.compile(
    r"\b(i|i'm|i've|i'd|my|me|i used to|honestly|for me)\b",
    re.I,
)

IMMERSIVE_YOU = re.compile(r"\byou\b", re.I)

OPERATING_RULES_BLOCK = """
YPP / INAUTHENTIC CONTENT — OPERATING RULES (counter demonetization & distribution throttling)

POLICY (Jul 2025): YouTube renamed "repetitious" → **inauthentic content**. AI tools are allowed;
mass-produced template output without human creative voice is not. Applies at **channel level**.

WHAT GETS FLAGGED (fully automated AI farms — often looks like "shadowban"):
- Template Shorts: identical hook/script skeleton, only keyword swapped (sleep → focus → anxiety)
- Slideshow + TTS with no story, commentary, or educational angle
- Scrolling text / image carousels with generic AI narration
- Reaction/recap clips with no original insight
- Batch uploads (multiple Shorts same day) — spam & deceptive practices signal
- Identical auto-comment replies at scale
- Engagement bait: ALL CAPS shock titles, "you won't believe", tag-stuffing
- Undisclosed realistic synthetic media presented as real footage
- Flat views after upload often = weak hook/retention OR duplicate-topic spam — do NOT re-upload same day

WHAT IS SAFE (Don't Blink / faceless creator channels):
- AI as production assistant: Gemini drafts, Resemble OWN voice clone, I2V horror clips per beat
- Immersive second-person horror micro-stories (singular you) OR first-person lived experience — not lecture mode
- ChainsFR minimal scenes — figure acts each beat, not one repeated room template
- Topic + hook cooldown (7–14 days), max 1 upload per 24h
- Quality gate + humanize pass before upload
- Light comment auto-reply; crisis/medical/collab → human queue
- Unlisted first → public after retention check (optional 24h)

BOT ENFORCEMENT (upload_guard — set YPP_SAFE_MODE=false to override):
- Blocks: spam-farm phrases, no personal voice (no you/I), >1 upload/24h, topic/hook cooldown, script overlap >65%
- auto_daily may render but **skips upload** when guard blocks
- Never auto-publish 5+ Shorts/day

HUMAN LAYER (counts as creative input for YPP):
- Serious comments, risky improvement approvals, niche positioning decisions
- Disclose altered/synthetic audio in Studio when prompted

Sources: support.google.com/youtube/answer/1311392 (inauthentic content policy).
"""


def risk_signals_for_script(script: str, hook: str, title: str) -> list[str]:
    """Return human-readable risk flags (empty = cleaner)."""
    risks: list[str] = []
    blob = f"{script} {hook}".lower()
    for phrase in SCRIPT_FARM_PHRASES:
        if phrase in blob:
            risks.append(f"spam-farm phrase: {phrase}")
    has_you = bool(IMMERSIVE_YOU.search(script))
    has_i = bool(FIRST_PERSON.search(script))
    if not has_you and not has_i:
        risks.append("missing personal voice (inauthentic lecture risk)")
    elif has_you and not has_i and len(script.split()) < 40:
        risks.append("thin second-person template — add specific wrong-detail beats")
    if len(script.split()) < 35:
        risks.append("script too short — thin template risk")
    for pat in TITLE_SPAM_PATTERNS:
        if pat.search(title):
            risks.append(f"spam title pattern: {pat.pattern[:40]}")
    if title.count("#") > 4:
        risks.append("title tag-stuffing")
    return risks
