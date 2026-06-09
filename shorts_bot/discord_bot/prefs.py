from __future__ import annotations

import json
from pathlib import Path

from shorts_bot.config import settings

PREFS_PATH = settings.data_dir / "discord_prefs.json"


def _load() -> dict:
    if not PREFS_PATH.exists():
        return {}
    try:
        return json.loads(PREFS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict) -> None:
    PREFS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREFS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def remember_dm_user(user_id: int) -> None:
    data = _load()
    data["last_dm_user_id"] = str(user_id)
    _save(data)


def briefing_user_ids() -> list[str]:
    ids = list(settings.discord_notify_list)
    if ids:
        return ids
    last = _load().get("last_dm_user_id")
    if last and str(last).isdigit():
        return [str(last)]
    return []
