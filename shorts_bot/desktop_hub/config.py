"""Desktop helper paths, token, and env loading."""

from __future__ import annotations

import os
from pathlib import Path

from shorts_bot.config import settings


def desktop_hub_dir() -> Path:
    path = settings.data_dir / "desktop_hub"
    path.mkdir(parents=True, exist_ok=True)
    return path


def helper_env_path() -> Path:
    return desktop_hub_dir() / "helper.env"


def schedule_path() -> Path:
    return desktop_hub_dir() / "schedule.json"


def daemon_pid_path() -> Path:
    return desktop_hub_dir() / "daemon.pid"


def load_helper_env_file() -> dict[str, str]:
    """Parse helper.env (KEY=value, one per line)."""
    path = helper_env_path()
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        val = val.strip().strip('"').strip("'")
        if key.strip() == "DESKTOP_HELPER_TOKEN":
            val = "".join(val.split())  # remove accidental spaces
        out[key.strip()] = val
    return out


def apply_helper_env() -> None:
    """Load helper.env into os.environ (does not override existing vars)."""
    for key, val in load_helper_env_file().items():
        os.environ.setdefault(key, val)


def resolve_token() -> str:
    apply_helper_env()
    return (os.environ.get("DESKTOP_HELPER_TOKEN") or "").strip()
