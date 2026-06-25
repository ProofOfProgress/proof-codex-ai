"""Parse work-duration directives from user messages."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Examples:
#   take an hour to respond
#   don't respond for 30 minutes
#   spend 2h on this
#   work for 45 min before answering
#   [1h] plan this week's shorts
#   respond in 90 minutes

_DURATION_PATTERNS: list[tuple[re.Pattern[str], int]] = [
    # bracket prefix: [1h], [30m], [2 hours]
    (
        re.compile(
            r"^\s*\[\s*(\d+(?:\.\d+)?)\s*"
            r"(hours|hour|hrs|hr|minutes|minute|mins|min|seconds|second|secs|sec|h|m|s)\s*\]\s*",
            re.I,
        ),
        1,
    ),
    # take/spend/work ... N unit ... (to respond|before|on)
    (
        re.compile(
            r"(?:take|spend|work|use)\s+(?:about\s+|around\s+|at\s+least\s+)?"
            r"(?:(?:an|a)\s+)?(\d+(?:\.\d+)?)\s*"
            r"(hours|hour|hrs|hr|minutes|minute|mins|min|seconds|second|secs|sec|h|m|s)"
            r"(?:\s+(?:to\s+)?(?:respond|reply|answer|work|research|think|before\s+(?:you\s+)?(?:respond|reply|answer)))?",
            re.I,
        ),
        1,
    ),
    # don't respond / wait N unit
    (
        re.compile(
            r"(?:don'?t|do\s+not)\s+respond\s+for\s+(\d+(?:\.\d+)?)\s*"
            r"(hours|hour|hrs|hr|minutes|minute|mins|min|seconds|second|secs|sec|h|m|s)",
            re.I,
        ),
        1,
    ),
    (
        re.compile(
            r"(?:wait|pause)\s+(\d+(?:\.\d+)?)\s*"
            r"(hours|hour|hrs|hr|minutes|minute|mins|min|seconds|second|secs|sec|h|m|s)"
            r"(?:\s+before\s+(?:responding|replying|answering))?",
            re.I,
        ),
        1,
    ),
    # respond in N unit
    (
        re.compile(
            r"respond\s+in\s+(\d+(?:\.\d+)?)\s*"
            r"(hours|hour|hrs|hr|minutes|minute|mins|min|seconds|second|secs|sec|h|m|s)",
            re.I,
        ),
        1,
    ),
    # an hour / a minute (standalone directive at start)
    (
        re.compile(
            r"^\s*(?:take\s+)?(?:an|a)\s+(hour|minute|min)\s+"
            r"(?:to\s+)?(?:respond|reply|answer|work|research)?\s*[-—:,]?\s*",
            re.I,
        ),
        0,  # special: group 0 is unit word only
    ),
]


def _unit_to_seconds(amount: float, unit: str) -> int:
    u = unit.lower().rstrip("s")
    if u in {"h", "hr", "hour"}:
        return int(amount * 3600)
    if u in {"m", "min", "minute"}:
        return int(amount * 60)
    if u in {"s", "sec", "second"}:
        return int(amount)
    return int(amount * 60)


@dataclass(frozen=True)
class ParsedDuration:
    """User message split into optional work budget + actual request."""

    cleaned_message: str
    work_seconds: int | None
    raw_directive: str | None = None

    @property
    def has_work_budget(self) -> bool:
        return self.work_seconds is not None and self.work_seconds > 0


def parse_work_duration(message: str) -> ParsedDuration:
    text = message.strip()
    if not text:
        return ParsedDuration("", None)

    for pattern, mode in _DURATION_PATTERNS:
        m = pattern.search(text)
        if not m:
            continue
        if mode == 0:
            unit_word = m.group(1).lower()
            amount = 1.0
            unit = "hour" if "hour" in unit_word else "minute"
            seconds = _unit_to_seconds(amount, unit)
            cleaned = (text[: m.start()] + text[m.end() :]).strip()
            return ParsedDuration(cleaned or text, seconds, m.group(0).strip())
        amount = float(m.group(1))
        unit = m.group(2)
        seconds = _unit_to_seconds(amount, unit)
        cleaned = (text[: m.start()] + text[m.end() :]).strip()
        # collapse duplicate whitespace / leading punctuation
        cleaned = re.sub(r"^[\s\-—:,]+", "", cleaned).strip()
        cleaned = re.sub(r"^to\s+", "", cleaned, flags=re.I).strip()
        return ParsedDuration(cleaned or text, seconds, m.group(0).strip())

    return ParsedDuration(text, None)


def clamp_work_seconds(seconds: int, *, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, seconds))


def format_duration(seconds: int) -> str:
    if seconds >= 3600:
        h = seconds / 3600
        return f"{h:.1f}h" if h % 1 else f"{int(h)}h"
    if seconds >= 120:
        m = seconds / 60
        return f"{m:.1f}m" if m % 1 else f"{int(m)}m"
    if seconds >= 60:
        return f"{seconds}s"
    return f"{seconds}s"
