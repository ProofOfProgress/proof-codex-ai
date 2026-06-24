"""Post queue — videos ready to ship per account."""

from __future__ import annotations

import json
from pathlib import Path

from shorts_bot.config import settings


def queue_path() -> Path:
    return settings.data_dir / "tiktok_shop" / "queue.json"


def load_queue() -> list[dict]:
    path = queue_path()
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def save_queue(rows: list[dict]) -> None:
    path = queue_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


def pending_posts(*, account_id: str | None = None) -> list[dict]:
    rows = [r for r in load_queue() if r.get("status", "pending") == "pending"]
    if account_id:
        rows = [r for r in rows if not r.get("account_id") or r.get("account_id") == account_id]
    return rows


def enqueue_video(
    *,
    video_path: str,
    product: str,
    caption: str,
    account_id: str = "",
) -> int:
    rows = load_queue()
    rows.append({
        "video_path": video_path,
        "product": product,
        "caption": caption,
        "account_id": account_id,
        "status": "pending",
    })
    save_queue(rows)
    return len(rows) - 1
