"""Queue uploads until YPP min gap clears, then schedule via YouTube API."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from shorts_bot.config import settings


@dataclass
class PendingUpload:
    draft_id: int
    video_path: str
    publish_at: str  # ISO UTC
    topic: str = ""
    created_at: str = ""

    def publish_dt(self) -> datetime:
        dt = datetime.fromisoformat(self.publish_at.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def video_file(self) -> Path:
        return Path(self.video_path)

    def video_exists(self) -> bool:
        return self.video_file().is_file()


def queue_path() -> Path:
    return settings.data_dir / "pending_uploads.json"


def load_queue() -> list[PendingUpload]:
    path = queue_path()
    if not path.is_file():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = raw if isinstance(raw, list) else raw.get("items") or []
    return [PendingUpload(**row) for row in items]


def save_queue(items: list[PendingUpload]) -> None:
    path = queue_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([asdict(i) for i in items], indent=2) + "\n",
        encoding="utf-8",
    )


def enqueue_upload(
    *,
    draft_id: int,
    video_path: Path,
    publish_at: datetime,
    topic: str = "",
) -> PendingUpload:
    if publish_at.tzinfo is None:
        publish_at = publish_at.replace(tzinfo=timezone.utc)
    publish_at = publish_at.astimezone(timezone.utc)
    item = PendingUpload(
        draft_id=draft_id,
        video_path=str(video_path.resolve()),
        publish_at=publish_at.isoformat(),
        topic=topic,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    items = [i for i in load_queue() if i.draft_id != draft_id]
    items.append(item)
    save_queue(items)
    return item


def process_due_uploads(*, force: bool = False) -> list[dict[str, Any]]:
    """Upload queued items when min gap + publish_at reached."""
    from shorts_bot.memory.extensions import MemoryExtensions
    from shorts_bot.memory.store import MemoryStore
    from shorts_bot.youtube.scheduled_upload import upload_scheduled_short

    store = MemoryStore(settings.database_path)
    mem = MemoryExtensions(store)
    now = datetime.now(timezone.utc)
    remaining: list[PendingUpload] = []
    results: list[dict[str, Any]] = []

    for item in load_queue():
        video = item.video_file()
        if not video.is_file():
            remaining.append(item)
            results.append(
                {
                    "draft_id": item.draft_id,
                    "ok": False,
                    "message": f"Missing MP4, keeping queued: {video}",
                    "retry": True,
                }
            )
            continue

        publish_at = item.publish_dt()
        recent = mem.recent_uploads(hours=48)
        gap_ok = True
        if recent and not force:
            last_at = datetime.fromisoformat(recent[0]["uploaded_at"].replace("Z", "+00:00"))
            if last_at.tzinfo is None:
                last_at = last_at.replace(tzinfo=timezone.utc)
            hours = (now - last_at).total_seconds() / 3600
            gap_ok = hours >= settings.min_hours_between_uploads

        due = force or (gap_ok and now >= publish_at - timedelta(minutes=5))
        if not due:
            remaining.append(item)
            continue

        try:
            url = upload_scheduled_short(
                item.draft_id,
                video,
                publish_at=max(publish_at, now),
                force=force,
            )
            results.append({"draft_id": item.draft_id, "ok": True, "url": url})
        except Exception as exc:
            msg = str(exc)[:300]
            if "max" in msg and "24h" in msg:
                remaining.append(item)
                results.append({"draft_id": item.draft_id, "ok": False, "message": msg, "retry": True})
            else:
                results.append({"draft_id": item.draft_id, "ok": False, "message": msg})

    save_queue(remaining)
    return results
