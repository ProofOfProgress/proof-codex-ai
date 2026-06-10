"""Immediate draft feedback learning — no second approval round."""

from __future__ import annotations

import re

from shorts_bot.memory.extensions import MemoryExtensions


def _slug(topic: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:50] or "topic"


def learn_from_draft(
    memory: MemoryExtensions,
    topic: str,
    reason: str,
    decision: str,
) -> str:
    """
    Write draft approve/reject directly to training_config.

    Rejections → avoid:* keys (immediate, used in next draft).
    Approvals → repeat:* keys (reinforce pattern).
    """
    note = (reason or "No reason given").strip()[:400]
    slug = _slug(topic)

    if decision == "rejected":
        key = f"avoid:{slug}"
        prev = memory.get_training_config(key) or ""
        merged = f"{prev}; {note}" if prev else note
        memory.set_training_config(key, merged[:500])
        return f"Learned avoid rule for «{topic[:60]}»"
    key = f"repeat:{slug}"
    memory.set_training_config(key, note[:500])
    return f"Learned repeat pattern for «{topic[:60]}»"
