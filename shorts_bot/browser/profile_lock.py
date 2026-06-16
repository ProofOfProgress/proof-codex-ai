"""Detect when the shared Chromium profile is locked by another session."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.config import settings


def browser_profile_locked(profile_dir: Path | None = None) -> tuple[bool, str]:
    """Return (locked, detail). Locked usually means owner Desktop browser is open."""
    profile = profile_dir or settings.browser_profile_dir
    if not profile.is_dir():
        return False, "profile missing"
    for name in ("SingletonLock", "SingletonSocket", "SingletonCookie"):
        if (profile / name).exists():
            return True, f"profile in use ({name}) — close Desktop browser or wait"
    return False, "profile available"


def require_unlocked_profile(*, action: str) -> None:
    locked, detail = browser_profile_locked()
    if locked:
        raise RuntimeError(
            f"Cannot {action}: browser profile locked ({detail}). "
            "Close the Desktop browser tab or finish the handoff, then retry."
        )
