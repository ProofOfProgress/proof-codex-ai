"""Phone hub worker — finish bubble inbox drafts (Mackenzie sound + publish).

Full UI automation requires physical phones. Until then, ``dry_run=True`` logs
each step so the pipeline can be tested end-to-end from cloud → Zernio draft → hub queue.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from shorts_bot.phone_hub.adb import AdbError, AdbResult, device_ready, run_adb
from shorts_bot.phone_hub.devices import resolve_serial
from shorts_bot.phone_hub.jobs import HubJob, next_pending_job, update_job

# Module 2 — Mackenzie sound (owner adds manually on phone until UI automation ships)
MACKENZIE_SOUND_URL = (
    "https://www.tiktok.com/music/original-sound-7418286946344340256"
)
MACKENZIE_SOUND_LABEL = "original sound - •Mackenzie•"

WORKER_STEPS = (
    "wake_device",
    "open_tiktok",
    "open_inbox",
    "open_draft",
    "add_mackenzie_sound",
    "publish",
)


@dataclass
class WorkerTickResult:
    action: str
    job_id: str = ""
    detail: str = ""
    dry_run: bool = True


def _run_step(
    job: HubJob,
    step: str,
    *,
    dry_run: bool,
    serial: str | None,
    adb_runner: Callable[..., AdbResult],
) -> tuple[bool, str]:
    if dry_run:
        return True, f"[dry-run] {step} on {job.phone_hub_slot} (serial={serial or 'unset'})"

    if not serial:
        return False, f"No adb_serial for {job.phone_hub_slot} — fill data/phone_hub/devices.json"

    if step == "wake_device":
        adb_runner("shell", "input", "keyevent", "KEYCODE_WAKEUP", serial=serial, check=True)
        return True, "device awake"

    if step == "open_tiktok":
        adb_runner(
            "shell",
            "monkey",
            "-p",
            "com.zhiliaoapp.musically",
            "-c",
            "android.intent.category.LAUNCHER",
            "1",
            serial=serial,
            check=True,
        )
        return True, "TikTok launched"

    # UI automation for inbox / Mackenzie / publish — needs phone + coordinate map
    return False, f"Step {step} not automated yet — finish manually on phone for now"


def run_job(
    job: HubJob,
    *,
    dry_run: bool = True,
    adb_runner: Callable[..., AdbResult] = run_adb,
) -> WorkerTickResult:
    serial = resolve_serial(job.phone_hub_slot)
    if not dry_run and serial and not device_ready(serial):
        update_job(job.id, status="awaiting_phone", detail=f"serial {serial} not in adb devices")
        return WorkerTickResult(
            action="awaiting_phone",
            job_id=job.id,
            detail=f"Phone {job.phone_hub_slot} not connected via USB",
            dry_run=dry_run,
        )

    update_job(job.id, status="in_progress")
    completed = list(job.steps_completed)

    for step in WORKER_STEPS:
        if step in completed:
            continue
        try:
            ok, detail = _run_step(job, step, dry_run=dry_run, serial=serial, adb_runner=adb_runner)
        except AdbError as exc:
            update_job(job.id, status="failed", detail=str(exc))
            return WorkerTickResult(action="failed", job_id=job.id, detail=str(exc), dry_run=dry_run)

        if not ok:
            update_job(job.id, status="awaiting_phone", detail=detail, steps_completed=completed)
            return WorkerTickResult(action="awaiting_phone", job_id=job.id, detail=detail, dry_run=dry_run)

        completed.append(step)
        update_job(job.id, steps_completed=completed, detail=detail)

    final_status = "dry_run_complete" if dry_run else "done"
    update_job(job.id, status=final_status, detail="all steps logged" if dry_run else "published")
    return WorkerTickResult(action=final_status, job_id=job.id, detail=job.account_id, dry_run=dry_run)


def tick(*, dry_run: bool = True) -> WorkerTickResult:
    job = next_pending_job()
    if not job:
        return WorkerTickResult(action="idle", detail="no pending hub jobs")
    return run_job(job, dry_run=dry_run)
