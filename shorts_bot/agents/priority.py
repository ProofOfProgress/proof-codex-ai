"""Work priority modes — what underlings focus on."""

from __future__ import annotations

from enum import Enum


class WorkPriority(str, Enum):
    RESEARCH = "research"
    BALANCED = "balanced"
    PRODUCTION = "production"


def parse_priority(value: str) -> WorkPriority:
    v = (value or "").strip().lower()
    for p in WorkPriority:
        if v == p.value:
            return p
    return WorkPriority.RESEARCH


def user_wants_drafts(user_request: str) -> bool:
    """Draft/script only when the human explicitly asks."""
    lower = user_request.lower()
    triggers = (
        "draft",
        "write script",
        "make video",
        "finish video",
        "produce",
        "script for",
        "create a short",
    )
    return any(t in lower for t in triggers)


def user_wants_research(user_request: str) -> bool:
    lower = user_request.lower()
    triggers = (
        "research",
        "plan",
        "score",
        "topic",
        "niche",
        "cosy",
        "cozy",
        "rpm",
        "hook",
        "competitor",
        "trend",
        "analyse",
        "analyze",
        "what should",
        "this week",
    )
    return any(t in lower for t in triggers)
