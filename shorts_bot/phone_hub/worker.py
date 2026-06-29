"""Phone hub worker — automated inbox finish on Android (bubble + affiliate)."""

from __future__ import annotations

import time

from dataclasses import dataclass
from typing import Callable

from shorts_bot.phone_hub.adb import AdbError, AdbResult, device_ready, run_adb
from shorts_bot.phone_hub.devices import resolve_serial
from shorts_bot.phone_hub.jobs import HubJob, next_pending_job, update_job
from shorts_bot.phone_hub.tiktok_finish import (
    MACKENZIE_SOUND_URL,
    add_mackenzie_sound,
    add_product_link,
    open_inbox,
    open_latest_draft,
    publish_draft,
)

MACKENZIE_SOUND_LABEL = "original sound - •Mackenzie•"

WORKER_STEPS_BUBBLE = (
    "wake_device",
    "open_tiktok",
    "open_inbox",
    "open_draft",
    "add_mackenzie_sound",
    "publish",
)

WORKER_STEPS_AFFILIATE = (
    "wake_device",
    "open_tiktok",
    "open_inbox",
    "open_draft",
    "add_product_link",
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

    slot = job.phone_hub_slot

    if step == "wake_device":
        adb_runner("shell", "input", "keyevent", "KEYCODE_WAKEUP", serial=serial, check=True)
        time.sleep(0.5)
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
        time.sleep(1.5)
        return True, "TikTok launched"

    if step == "open_inbox":
        return open_inbox(serial=serial, slot=slot)

    if step == "open_draft":
        return open_latest_draft(serial=serial, slot=slot)

    if step == "add_mackenzie_sound":
        return add_mackenzie_sound(serial=serial, slot=slot)

    if step == "add_product_link":
        return add_product_link(serial=serial, slot=slot, product_name=job.product_name)

    if step == "publish":
        return publish_draft(serial=serial, slot=slot)

    return False, f"unknown step: {step}"


def run_job(
    job: HubJob,
    *,
    dry_run: bool = True,
    adb_runner: Callable[..., AdbResult] = run_adb,
) -> WorkerTickResult:
    serial = resolve_serial(job.phone_hub_slot)
    if not dry_run and not serial:
        update_job(job.id, status="awaiting_phone", detail=f"No adb_serial for {job.phone_hub_slot}")
        return WorkerTickResult(
            action="awaiting_phone",
            job_id=job.id,
            detail=f"Fill adb_serial in devices.json for {job.phone_hub_slot}",
            dry_run=dry_run,
        )
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
    steps = WORKER_STEPS_AFFILIATE if job.job_type == "affiliate" else WORKER_STEPS_BUBBLE

    for step in steps:
        if step in completed:
            continue
        try:
            ok, detail = _run_step(job, step, dry_run=dry_run, serial=serial, adb_runner=adb_runner)
        except AdbError as exc:
            update_job(job.id, status="failed", detail=str(exc))
            return WorkerTickResult(action="failed", job_id=job.id, detail=str(exc), dry_run=dry_run)

        if not ok:
            update_job(job.id, status="failed", detail=detail, steps_completed=completed)
            return WorkerTickResult(action="failed", job_id=job.id, detail=detail, dry_run=dry_run)

        completed.append(step)
        update_job(job.id, steps_completed=completed, detail=detail)

    final_status = "dry_run_complete" if dry_run else "done"
    update_job(job.id, status=final_status, detail="published" if not dry_run else "dry-run ok")
    return WorkerTickResult(action=final_status, job_id=job.id, detail=job.account_id, dry_run=dry_run)


def tick(*, dry_run: bool = True, slot: str | None = None, only_connected: bool = False) -> WorkerTickResult:
    job = next_pending_job(slot=slot, only_connected=only_connected)
    if not job:
        detail = "no pending hub jobs"
        if slot:
            detail += f" for {slot}"
        if only_connected:
            detail += " (connected phones only)"
        return WorkerTickResult(action="idle", detail=detail)
    return run_job(job, dry_run=dry_run)


def run_until_idle(
    *,
    dry_run: bool = False,
    max_jobs: int = 20,
    slot: str | None = None,
    only_connected: bool = False,
) -> list[WorkerTickResult]:
    """Process pending hub jobs sequentially (hub daemon / cron)."""
    results: list[WorkerTickResult] = []
    for _ in range(max_jobs):
        result = tick(dry_run=dry_run, slot=slot, only_connected=only_connected)
        results.append(result)
        if result.action == "idle":
            break
        if result.action == "failed":
            break
    return results
