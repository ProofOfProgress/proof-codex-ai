"""Codex — Shorts Bot knowledge base (course, research, brand, learned rules)."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.course.loader import CourseKnowledgeBase

CODEX_NAME = "Codex"

# Jenny strategist files 01–09 under course/files/
CODEX_COURSE_ROOT = Path("course")

CODEX_BLURB = (
    "Codex is the project's knowledge base — Jenny Hoyos strategist files (01–09), "
    "brand/world docs, horror research, and self-learned rules. "
    "BM25 search is internal: AlphaBeta001 + cloud agents only (not owner-facing)."
)


def load_codex(course_dir: Path | None = None) -> CourseKnowledgeBase:
    """Load Codex course corpus (files 01–09 + verbatim)."""
    return CourseKnowledgeBase(course_dir or CODEX_COURSE_ROOT)


__all__ = [
    "CODEX_NAME",
    "CODEX_BLURB",
    "CODEX_COURSE_ROOT",
    "CourseKnowledgeBase",
    "load_codex",
]
