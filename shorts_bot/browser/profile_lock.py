"""Detect when the shared Chromium profile is locked by another session."""

from __future__ import annotations

import os
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


def clear_stale_profile_lock(profile_dir: Path | None = None) -> bool:
    """Remove lock files if the locking process is gone. Returns True if cleared."""
    profile = profile_dir or settings.browser_profile_dir
    if not profile.is_dir():
        return False

    locked, _ = browser_profile_locked()
    if not locked:
        return False

    pid = None
    lock = profile / "SingletonLock"
    try:
        target = os.readlink(lock)
        if target.startswith("cursor-"):
            pid = int(target.split("-", 1)[1])
    except OSError:
        target = ""

    if pid is not None:
        try:
            os.kill(pid, 0)
            return False  # still running
        except OSError:
            pass

    cleared = False
    for name in ("SingletonLock", "SingletonSocket", "SingletonCookie"):
        path = profile / name
        if path.exists() or path.is_symlink():
            try:
                path.unlink(missing_ok=True)
                cleared = True
            except OSError:
                pass
    return cleared


def require_unlocked_profile(*, action: str) -> None:
    clear_stale_profile_lock()
    locked, detail = browser_profile_locked()
    if locked:
        raise RuntimeError(
            f"Cannot {action}: browser profile locked ({detail}). "
            "Close the Desktop browser tab or finish the handoff, then retry."
        )
