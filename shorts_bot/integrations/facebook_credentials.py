"""Facebook API credentials — Cursor secrets, .env, or local data/facebook_api.json."""

from __future__ import annotations

import json
from pathlib import Path

from shorts_bot.config import settings


def credentials_path() -> Path:
    return settings.data_dir / "facebook_api.json"


def load_facebook_api_file() -> dict[str, str]:
    path = credentials_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return {str(k): str(v) for k, v in data.items() if v}


def save_facebook_api_file(
    *,
    page_id: str,
    page_access_token: str = "",
    page_name: str = "",
) -> Path:
    path = credentials_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_facebook_api_file()
    payload = {
        "page_id": page_id.strip() or existing.get("page_id", ""),
        "page_access_token": page_access_token.strip() or existing.get("page_access_token", ""),
        "page_name": page_name.strip() or existing.get("page_name", ""),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if payload["page_id"] and payload["page_access_token"]:
        _upsert_env(page_id=payload["page_id"], token=payload["page_access_token"])
    return path


def _upsert_env(*, page_id: str, token: str) -> None:
    env_path = Path(".env")
    if not env_path.is_file():
        return
    lines = env_path.read_text(encoding="utf-8").splitlines()
    updates = {
        "FACEBOOK_PAGE_ID": page_id,
        "META_PAGE_ACCESS_TOKEN": token,
    }
    for key, value in updates.items():
        pattern_found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                pattern_found = True
                break
        if not pattern_found:
            lines.append(f"{key}={value}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def resolve_facebook_credentials() -> tuple[str, str, str]:
    """Return (page_id, page_access_token, source_label)."""
    pid = (settings.facebook_page_id or "").strip()
    token = (settings.meta_page_access_token or "").strip()
    if pid and token:
        return pid, token, "env"
    data = load_facebook_api_file()
    pid = (data.get("page_id") or "").strip()
    token = (data.get("page_access_token") or "").strip()
    if pid and token:
        return pid, token, "facebook_api.json"
    return "", "", "missing"
