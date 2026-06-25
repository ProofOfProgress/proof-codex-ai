"""Reflexio-style learning from owner chat — no extra auth."""

from __future__ import annotations

import re

from shorts_bot.config import settings
from shorts_bot.learning.mem0_bridge import remember
from shorts_bot.memory.extensions import MemoryExtensions

_AVOID = re.compile(
    r"\b(avoid|don'?t|stop|never|framing was|wonky|too generic|don'?t use)\b",
    re.I,
)
_REPEAT = re.compile(
    r"\b(more like|do again|worked|keep this|double down|that hook)\b",
    re.I,
)


def capture_owner_signal(memory: MemoryExtensions, message: str) -> str | None:
    """
    Learn from plain-English owner feedback in chat.
    Returns short confirmation or None if no signal detected.
    """
    if not settings.owner_signals_enabled:
        return None
    text = message.strip()
    if len(text) < 12 or len(text) > 800:
        return None
    if text.startswith(("http://", "https://", "dev:", "yes ", "no ", "draft ")):
        return None

    if _AVOID.search(text):
        key = f"avoid:owner:{text[:60].lower()}"
        memory.set_training_config(key, text[:400])
        remember(f"Owner avoid: {text[:300]}", metadata={"type": "owner_avoid", "source": "chat"})
        return "Noted — I'll avoid that pattern on future scripts."

    if _REPEAT.search(text):
        key = f"repeat:owner:{text[:60].lower()}"
        memory.set_training_config(key, text[:400])
        remember(f"Owner repeat: {text[:300]}", metadata={"type": "owner_repeat", "source": "chat"})
        return "Noted — I'll repeat that when it fits."

    return None
