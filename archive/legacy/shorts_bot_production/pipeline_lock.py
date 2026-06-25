"""Exclusive lock — one finish_cli / Replicate I2V job at a time."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.config import settings


@dataclass
class LockInfo:
    draft_id: int
    pid: int
    started_at: str

    @classmethod
    def from_dict(cls, data: dict) -> LockInfo:
        return cls(
            draft_id=int(data.get("draft_id", 0)),
            pid=int(data.get("pid", 0)),
            started_at=str(data.get("started_at") or ""),
        )


def lock_path() -> Path:
    return settings.data_dir / "production" / ".pipeline.lock"


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def read_lock() -> LockInfo | None:
    path = lock_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        info = LockInfo.from_dict(data)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None
    if not _pid_alive(info.pid):
        path.unlink(missing_ok=True)
        return None
    return info


def acquire_lock(draft_id: int) -> bool:
    """Return True if lock acquired."""
    if not settings.pipeline_exclusive_lock:
        return True
    existing = read_lock()
    if existing and existing.pid != os.getpid():
        return False
    path = lock_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "draft_id": draft_id,
                "pid": os.getpid(),
                "started_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return True


def release_lock(draft_id: int | None = None) -> None:
    info = read_lock()
    if info is None:
        return
    if draft_id is not None and info.draft_id != draft_id:
        return
    if info.pid != os.getpid():
        return
    lock_path().unlink(missing_ok=True)


@contextmanager
def pipeline_lock(draft_id: int):
    if not acquire_lock(draft_id):
        info = read_lock()
        holder = f"draft #{info.draft_id} pid {info.pid}" if info else "unknown"
        raise RuntimeError(
            f"Pipeline lock held by {holder}. "
            "Only one finish_cli at a time (Replicate 429 avoidance)."
        )
    try:
        yield
    finally:
        release_lock(draft_id)
