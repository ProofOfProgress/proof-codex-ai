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
    uid = str(user_id)
    data["last_dm_user_id"] = uid
    users = {str(u) for u in data.get("dm_users", [])}
    users.add(uid)
    data["dm_users"] = sorted(users)
    _save(data)


def briefing_user_ids() -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for uid in settings.discord_notify_list:
        if uid.isdigit() and uid not in seen:
            seen.add(uid)
            out.append(uid)
    data = _load()
    for uid in data.get("dm_users", []):
        s = str(uid)
        if s.isdigit() and s not in seen:
            seen.add(s)
            out.append(s)
    if not out:
        last = data.get("last_dm_user_id")
        if last and str(last).isdigit():
            out.append(str(last))
    return out


def briefing_already_sent_today() -> bool:
    from datetime import date

    return _load().get("briefing_date") == date.today().isoformat()


def mark_briefing_sent_today() -> None:
    from datetime import date

    data = _load()
    data["briefing_date"] = date.today().isoformat()
    _save(data)
