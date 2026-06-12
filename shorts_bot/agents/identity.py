"""Agent identity — manager display name (not the YouTube channel)."""

from __future__ import annotations

from shorts_bot.config import settings


def manager_name() -> str:
    """Human-facing name for the Chief Manager agent."""
    return (settings.manager_display_name or "AlphaBeta001").strip()


def manager_intro_line() -> str:
    """One line for CLI/web — manager vs channel."""
    return f"{manager_name()} — Chief Manager for Peripheral"
