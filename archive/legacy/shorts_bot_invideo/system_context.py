"""Load and wrap InVideo master system context for every API/browser prompt."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_BRIEF_SEPARATOR = "\n\n--- VIDEO BRIEF ---\n\n"
_MASTER_PATH = Path(__file__).with_name("invideo_master_prompt.md")


@lru_cache(maxsize=1)
def load_master_context() -> str:
    if not _MASTER_PATH.is_file():
        raise FileNotFoundError(f"Missing InVideo master prompt: {_MASTER_PATH}")
    return _MASTER_PATH.read_text(encoding="utf-8").strip()


def wrap_invideo_prompt(brief: str, *, include_master: bool = True) -> str:
    """
    Prepend full channel context to a per-video brief for InVideo MCP / Agent One.
    InVideo receives everything it needs to act as this channel's filmmaker.
    """
    brief = brief.strip()
    if not include_master:
        return brief
    master = load_master_context()
    if not brief:
        return master
    return f"{master}{_BRIEF_SEPARATOR}{brief}"


def brief_only_for_display(full_prompt: str) -> str:
    """Extract the per-video brief from a wrapped prompt (for logs/UI)."""
    if _BRIEF_SEPARATOR in full_prompt:
        return full_prompt.split(_BRIEF_SEPARATOR, 1)[1].strip()
    return full_prompt.strip()
