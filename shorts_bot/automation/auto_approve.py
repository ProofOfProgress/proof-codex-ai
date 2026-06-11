"""Auto-approve low-risk improvements and dev tasks (no human Yes/No)."""

from __future__ import annotations

import re

from shorts_bot.config import settings
from shorts_bot.memory.extensions import DevTask, Improvement, MemoryExtensions

SAFE_IMPROVEMENT_CATEGORIES = frozenset({"hook", "retention", "drafting", "editing", "cta"})
RISKY_TEXT = re.compile(
    r"\b(login|oauth|password|payment|subscribe to paid|credit card|delete channel|change niche|"
    r"stop upload|new channel|vidIQ|turboscribe account|resemble account)\b",
    re.I,
)


def improvement_is_auto_approvable(imp: Improvement) -> bool:
    if not settings.auto_approve_improvements:
        return False
    if imp.source.startswith("feedback:"):
        return True
    if imp.category not in SAFE_IMPROVEMENT_CATEGORIES:
        return False
    blob = f"{imp.title} {imp.description}"
    if RISKY_TEXT.search(blob):
        return False
    if imp.source.startswith("reward:punish:"):
        return imp.category in ("hook", "retention", "editing")
    if imp.source.startswith("reward:reward:"):
        return imp.category in ("hook", "retention")
    return imp.category in ("hook", "retention", "drafting", "editing", "cta")


def dev_task_is_auto_approvable(task: DevTask) -> bool:
    if not settings.auto_approve_dev_tasks:
        return False
    blob = f"{task.title} {task.description}"
    if RISKY_TEXT.search(blob):
        return False
    return True
