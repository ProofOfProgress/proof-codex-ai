"""Process phone_queue.json — Mackenzie carousel posts with account switching."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok.adb_carousel import post_carousel_with_sound
from shorts_bot.tiktok.phone_queue import (
    PhonePostJob,
    STATUS_DONE,
    STATUS_FAILED,
    STATUS_PENDING,
    STATUS_RUNNING,
    load_queue,
    pending_jobs,
    save_queue,
    update_job,
)


@dataclass
class WorkerRunResult:
    processed: int
    succeeded: int
    failed: int
    messages: list[str]


def _resolve_slide(path_str: str) -> Path:
    p = Path(path_str)
    if p.is_file():
        return p
    # Allow repo-relative paths from cloud agent commits.
    from shorts_bot.config import settings as cfg

    alt = cfg.data_dir.parent / path_str
    if alt.is_file():
        return alt
    alt2 = Path(path_str).expanduser()
    if alt2.is_file():
        return alt2
    raise FileNotFoundError(path_str)


def run_pending_jobs(
    *,
    device_id: str | None = None,
    dry_run: bool = False,
    max_jobs: int | None = None,
) -> WorkerRunResult:
    jobs = pending_jobs()
    if max_jobs is not None:
        jobs = jobs[:max_jobs]

    messages: list[str] = []
    ok_count = 0
    fail_count = 0

    pause = max(10, int(settings.phone_worker_pause_between_accounts_sec))

    for job in jobs:
        update_job(job.id, status=STATUS_RUNNING, error="")
        try:
            slide1 = _resolve_slide(job.slide1)
            slide2 = _resolve_slide(job.slide2)
            result = post_carousel_with_sound(
                [slide1, slide2],
                sound_id=job.sound_id,
                device_id=device_id,
                switch_label=job.switch_label,
                dry_run=dry_run,
            )
            if result.ok:
                update_job(
                    job.id,
                    status=STATUS_DONE,
                    steps=result.steps,
                    error="",
                )
                ok_count += 1
                messages.append(f"OK {job.account_id}: {result.message}")
            else:
                update_job(job.id, status=STATUS_FAILED, error=result.message)
                fail_count += 1
                messages.append(f"FAIL {job.account_id}: {result.message}")
        except Exception as exc:  # noqa: BLE001
            update_job(job.id, status=STATUS_FAILED, error=str(exc))
            fail_count += 1
            messages.append(f"FAIL {job.account_id}: {exc}")

        if not dry_run and len(jobs) > 1:
            time.sleep(pause)

    return WorkerRunResult(
        processed=len(jobs),
        succeeded=ok_count,
        failed=fail_count,
        messages=messages,
    )


def enqueue_bubble_jobs(
    packs: list[dict[str, str]],
    *,
    accounts_by_id: dict[str, object],
) -> list[PhonePostJob]:
    """Enqueue carousel jobs from batch pack definitions."""
    from shorts_bot.tiktok.phone_queue import enqueue_job
    from shorts_bot.tiktok.sounds import MACKENZIE_SOUND_ID

    created: list[PhonePostJob] = []
    for pack in packs:
        account = accounts_by_id.get(pack["account_id"])
        if account is None:
            continue
        switch_label = (
            getattr(account, "tiktok_switch_label", None)
            or getattr(account, "label", "")
            or pack["account_id"]
        )
        job = enqueue_job(
            account_id=pack["account_id"],
            switch_label=str(switch_label),
            slide1=Path(pack["slide1"]),
            slide2=Path(pack["slide2"]),
            sound_id=MACKENZIE_SOUND_ID,
        )
        created.append(job)
    return created


def queue_summary() -> dict[str, int]:
    jobs = load_queue()
    counts = {STATUS_PENDING: 0, STATUS_RUNNING: 0, STATUS_DONE: 0, STATUS_FAILED: 0}
    for job in jobs:
        counts[job.status] = counts.get(job.status, 0) + 1
    return counts
