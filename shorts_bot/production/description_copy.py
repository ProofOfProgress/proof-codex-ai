"""Public-facing upload copy — no jumpscare spoilers in descriptions."""

from __future__ import annotations

import re

# Finale drafts: hint at end payoff without saying "jumpscare".
FINALE_VOLUME_WARNING = (
    "🔊 VOLUME WARNING — loud moment at the end. Headphones advised."
)

FINALE_STORY_TEASE = (
    "One impossible detail → tension → watch to the end."
)

SUSPENSE_STORY_TEASE = (
    "One impossible detail → tension → replay to catch what you missed."
)

_DESCRIPTION_SPOILERS = (
    "jumpscare",
    "jump scare",
    "jumpscare near the end",
    "jumpscare at the end",
    "scare at the end",
    "scare near the end",
)


def description_is_safe(text: str) -> bool:
    lower = (text or "").lower()
    return not any(phrase in lower for phrase in _DESCRIPTION_SPOILERS)


def sanitize_description_text(text: str) -> str:
    """Strip/replace spoiler phrases in titles, descriptions, volume lines."""
    if not text:
        return text
    out = text
    replacements = [
        (r"jumpscare\s+near\s+the\s+end", "loud moment at the end"),
        (r"jumpscare\s+at\s+the\s+end", "something at the end"),
        (r"jump\s+scare\s+near\s+the\s+end", "loud moment at the end"),
        (r"scare\s+at\s+the\s+end", "payoff at the end"),
        (r"scare\s+near\s+the\s+end", "moment at the end"),
        (r"\bjumpscare\b", "payoff"),
        (r"\bjump\s+scare\b", "payoff"),
    ]
    for pattern, repl in replacements:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out


def volume_warning_for_plan(*, has_jumpscare: bool, raw_warning: str = "") -> str:
    """Volume line for description — empty on suspense-replay drafts."""
    if not has_jumpscare:
        return ""
    line = (raw_warning or FINALE_VOLUME_WARNING).strip()
    line = sanitize_description_text(line)
    if not line.startswith("🔊") and line:
        line = f"🔊 {line}"
    return line


def story_tease_line(*, has_jumpscare: bool) -> str:
    return FINALE_STORY_TEASE if has_jumpscare else SUSPENSE_STORY_TEASE
