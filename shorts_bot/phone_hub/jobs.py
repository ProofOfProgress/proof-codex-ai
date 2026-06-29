"""File-based queue of hub jobs — finish Zernio inbox drafts on the correct phone."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class HubJob:
    id: str
    account_id: str
    phone_hub_slot: str
    zernio_post_id: str
    slide1: str
    slide2: str
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    detail: str = ""
    steps_completed: list[str] = field(default_factory=list)


def jobs_path() -> Path:
    return settings.data_dir / "phone_hub" / "pending_jobs.jsonl"


def _read_jobs() -> list[HubJob]:
    path = jobs_path()
    if not path.is_file():
        return []
    jobs: list[HubJob] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        jobs.append(HubJob(**row))
    return jobs


def _write_jobs(jobs: list[HubJob]) -> None:
    path = jobs_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for job in jobs:
            f.write(json.dumps(asdict(job)) + "\n")


def enqueue_job(
    *,
    account_id: str,
    phone_hub_slot: str,
    zernio_post_id: str,
    slide1: str | Path,
    slide2: str | Path,
    status: str = "pending",
    detail: str = "",
) -> HubJob:
    jobs = _read_jobs()
    job = HubJob(
        id=uuid.uuid4().hex[:12],
        account_id=account_id,
        phone_hub_slot=phone_hub_slot,
        zernio_post_id=zernio_post_id,
        slide1=str(slide1),
        slide2=str(slide2),
        status=status,
        detail=detail,
    )
    jobs.append(job)
    _write_jobs(jobs)
    return job


def list_jobs(*, status: str | None = None) -> list[HubJob]:
    jobs = _read_jobs()
    if status:
        jobs = [j for j in jobs if j.status == status]
    return jobs


def update_job(job_id: str, **fields: object) -> HubJob | None:
    jobs = _read_jobs()
    updated: HubJob | None = None
    for i, job in enumerate(jobs):
        if job.id != job_id:
            continue
        data = asdict(job)
        data.update(fields)
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        updated = HubJob(**data)
        jobs[i] = updated
        break
    if updated:
        _write_jobs(jobs)
    return updated


def next_pending_job() -> HubJob | None:
    for job in list_jobs(status="pending"):
        return job
    return None
