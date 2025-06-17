"""Validate codex entries against Proof Codex laws."""

from pathlib import Path
from typing import Iterable

from .codex_task_parser import CodexEntry


VALID_TAGS = {"LAW", "SYSTEM", "PROMPT", "PILLAR"}


def validate_entries(entries: Iterable[CodexEntry]) -> None:
    """Raise ValueError if any entry does not comply with Codex rules."""
    for entry in entries:
        if entry.tag not in VALID_TAGS:
            raise ValueError(f"Invalid tag: {entry.tag}")
        if not entry.content.strip():
            raise ValueError("Entry content cannot be empty")
