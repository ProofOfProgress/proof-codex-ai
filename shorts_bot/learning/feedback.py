"""Immediate draft feedback learning — no second approval round + episodic consolidation."""

from __future__ import annotations

import re

from shorts_bot.training.auto_approve import improvement_is_auto_approvable
from shorts_bot.config import settings
from shorts_bot.learning.learned_file import LearnedFile
from shorts_bot.learning.reflect import consolidate_draft_feedback
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.training.proposer import ImprovementProposer


def _slug(topic: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:50] or "topic"


def learn_from_draft(
    memory: MemoryExtensions,
    topic: str,
    reason: str,
    decision: str,
    *,
    proposer: ImprovementProposer | None = None,
    auto_approve_feedback: bool = True,
) -> str:
    """
    Write draft approve/reject directly to training_config.

    Rejections → avoid:* keys (immediate, used in next draft).
    Approvals → repeat:* keys (reinforce pattern).
    Also creates improvement proposal + episodic reflection when self-training on.
    """
    note = (reason or "No reason given").strip()[:400]
    slug = _slug(topic)

    if decision == "rejected":
        key = f"avoid:{slug}"
        prev = memory.get_training_config(key) or ""
        merged = f"{prev}; {note}" if prev else note
        memory.set_training_config(key, merged[:500])
        base_msg = f"Learned avoid rule for «{topic[:60]}»"
    else:
        key = f"repeat:{slug}"
        memory.set_training_config(key, note[:500])
        base_msg = f"Learned repeat pattern for «{topic[:60]}»"

    extra = ""
    if settings.self_training_enabled:
        consolidate_draft_feedback(memory, topic=topic, reason=note, decision=decision)
        prop = proposer or ImprovementProposer(memory, client=None)
        imp = prop.propose_from_feedback(topic, note, decision)
        if auto_approve_feedback and improvement_is_auto_approvable(imp):
            memory.review_improvement(imp.id, approved=True, note="Auto-approved (draft feedback)")
            LearnedFile(settings.learned_path).record_improvement(
                memory.get_improvement(imp.id),
                approved=True,
            )
            extra = f"; improvement #{imp.id} auto-applied"

    return base_msg + extra
