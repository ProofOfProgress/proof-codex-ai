"""Public-facing upload copy — plain 5th–8th grade language."""

from __future__ import annotations

import re

FINALE_VOLUME_WARNING = (
    "🔊 VOLUME WARNING — jumpscare at the end. Use headphones."
)

FINALE_STORY_TEASE = (
    "Scary stories in about 30 seconds. Watch to the end."
)

SUSPENSE_STORY_TEASE = (
    "Scary stories in about 30 seconds. The ending might surprise you."
)

# Channel copy should never use jargon like this.
_BANNED_PUBLIC_PHRASES = (
    "impossible detail",
    "micro-story",
    "micro-stories",
    "payoff",
    "terrifying faceless",
)


def description_is_safe(text: str) -> bool:
    lower = (text or "").lower()
    return not any(phrase in lower for phrase in _BANNED_PUBLIC_PHRASES)


def sanitize_description_text(text: str) -> str:
    """Normalize legacy copy to plain wording — jumpscare is fine to say out loud."""
    if not text:
        return text
    out = text
    replacements = [
        (
            r"one\s+impossible\s+detail\s*→\s*tension\s*→\s*watch\s+to\s+the\s+end\.?",
            FINALE_STORY_TEASE,
        ),
        (
            r"one\s+impossible\s+detail\s*→\s*tension\s*→\s*replay\s+to\s+catch\s+what\s+you\s+missed\.?",
            SUSPENSE_STORY_TEASE,
        ),
        (r"impossible\s+detail", "something wrong"),
        (r"loud\s+moment\s+at\s+the\s+end", "jumpscare at the end"),
        (r"jumpscare\s+near\s+the\s+end", "jumpscare at the end"),
        (r"jump\s+scare\s+near\s+the\s+end", "jumpscare at the end"),
        (r"\bscare\s+at\s+the\s+end", "jumpscare at the end"),
        (r"\bscare\s+near\s+the\s+end", "jumpscare at the end"),
        (r"payoff\s+at\s+the\s+end", "jumpscare at the end"),
        (r"\bpayoff\b", "jumpscare"),
        (
            r"terrifying\s+faceless\s+horror\s+micro-stories",
            "scary horror Shorts",
        ),
        (r"headphones\s+advised", "use headphones"),
    ]
    for pattern, repl in replacements:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    out = re.sub(r"\bjumpjumpjumpscare\b", "jumpscare", out, flags=re.IGNORECASE)
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
