"""Load gitignored hub credentials into os.environ (Kalodata, Discord, course)."""

from __future__ import annotations

import os
from pathlib import Path

from shorts_bot.config import settings

_LOADED = False


def credentials_path() -> Path:
    return settings.data_dir / "agent_credentials.env"


def load_agent_credentials(*, force: bool = False) -> Path | None:
    """Merge data/agent_credentials.env into os.environ once."""
    global _LOADED
    if _LOADED and not force:
        return credentials_path() if credentials_path().is_file() else None

    path = credentials_path()
    if not path.is_file():
        _LOADED = True
        return None

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and val and key not in os.environ:
            os.environ[key] = val

    _LOADED = True
    return path


def credential_keys() -> list[str]:
    path = credentials_path()
    if not path.is_file():
        return []
    keys: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            keys.append(line.partition("=")[0].strip())
    return keys
