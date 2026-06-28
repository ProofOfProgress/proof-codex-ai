"""JSON job queue for local phone worker (Mackenzie carousel posts)."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shorts_bot.config import settings

STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_DONE = "done"
STATUS_FAILED = "failed"


@dataclass
class PhonePostJob:
    id: str
    account_id: str
    switch_label: str
    slide1: str
    slide2: str
    sound_id: str
    status: str = STATUS_PENDING
    created_at: str = ""
    updated_at: str = ""
    error: str = ""
    steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> PhonePostJob:
        return cls(
            id=str(raw.get("id") or ""),
            account_id=str(raw.get("account_id") or ""),
            switch_label=str(raw.get("switch_label") or ""),
            slide1=str(raw.get("slide1") or ""),
            slide2=str(raw.get("slide2") or ""),
            sound_id=str(raw.get("sound_id") or ""),
            status=str(raw.get("status") or STATUS_PENDING),
            created_at=str(raw.get("created_at") or ""),
            updated_at=str(raw.get("updated_at") or ""),
            error=str(raw.get("error") or ""),
            steps=list(raw.get("steps") or []),
        )


def queue_path() -> Path:
    return settings.phone_queue_path


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_queue(path: Path | None = None) -> list[PhonePostJob]:
    p = path or queue_path()
    if not p.is_file():
        return []
    raw = json.loads(p.read_text(encoding="utf-8"))
    rows = raw.get("jobs") if isinstance(raw, dict) else raw
    if not isinstance(rows, list):
        return []
    return [PhonePostJob.from_dict(row) for row in rows if isinstance(row, dict)]


def save_queue(jobs: list[PhonePostJob], path: Path | None = None) -> Path:
    p = path or queue_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {"jobs": [j.to_dict() for j in jobs], "updated_at": _now_iso()}
    p.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return p


def enqueue_job(
    *,
    account_id: str,
    switch_label: str,
    slide1: Path,
    slide2: Path,
    sound_id: str,
    path: Path | None = None,
) -> PhonePostJob:
    jobs = load_queue(path)
    job = PhonePostJob(
        id=f"phone_{uuid.uuid4().hex[:12]}",
        account_id=account_id,
        switch_label=switch_label,
        slide1=str(slide1.resolve()),
        slide2=str(slide2.resolve()),
        sound_id=sound_id,
        status=STATUS_PENDING,
        created_at=_now_iso(),
        updated_at=_now_iso(),
    )
    jobs.append(job)
    save_queue(jobs, path)
    return job


def pending_jobs(path: Path | None = None) -> list[PhonePostJob]:
    return [j for j in load_queue(path) if j.status == STATUS_PENDING]


def update_job(job_id: str, **fields: Any) -> PhonePostJob | None:
    jobs = load_queue()
    for idx, job in enumerate(jobs):
        if job.id != job_id:
            continue
        data = job.to_dict()
        data.update(fields)
        data["updated_at"] = _now_iso()
        jobs[idx] = PhonePostJob.from_dict(data)
        save_queue(jobs)
        return jobs[idx]
    return None
