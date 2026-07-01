"""Bubble wrap scheduler — Zernio inbox draft + hub job queue (phones finish Mackenzie)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.phone_hub.jobs import enqueue_job, list_jobs
from shorts_bot.tiktok_shop.accounts import ShopAccount, bubble_accounts, load_account
from shorts_bot.tiktok_shop.bubble_batch import DEFAULT_BUBBLE_SUBJECTS
from shorts_bot.tiktok_shop.bubble_wrap import generate_bubble_wrap_slides
from shorts_bot.tiktok_shop.bubble_wrap_post import post_bubble_wrap_carousel
from shorts_bot.tiktok_shop.quota import log_post, posts_today, remaining_today
from shorts_bot.tiktok_shop.scheduler import seconds_until_next_post

MAX_PENDING_HUB_JOBS = 1


def bubble_scheduler_log_path() -> Path:
    return settings.data_dir / "phone_hub" / "scheduler_log.jsonl"


def log_bubble_tick(*, account_id: str, action: str, detail: str = "") -> None:
    path = bubble_scheduler_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "at": datetime.now(timezone.utc).isoformat(),
        "account_id": account_id,
        "action": action,
        "detail": detail[:500],
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


@dataclass
class BubbleTickResult:
    account_id: str
    action: str
    detail: str = ""
    subject: str = ""
    post_id: str = ""
    hub_job_id: str = ""


def pick_bubble_subject(account_id: str) -> str:
    """Rotate subjects per account so clips stay varied."""
    subjects = list(DEFAULT_BUBBLE_SUBJECTS)
    if not subjects:
        return "frog"
    offset = sum(ord(c) for c in account_id) % len(subjects)
    idx = (posts_today(account_id) + offset) % len(subjects)
    return subjects[idx]


def pending_hub_jobs_for(account_id: str) -> int:
    return sum(1 for j in list_jobs(status="pending") if j.account_id == account_id)


def pick_bubble_account(*, account_id: str | None = None) -> ShopAccount | None:
    if account_id:
        acct = load_account(account_id)
        return acct if acct and acct.track.startswith("bubble") and acct.enabled else None
    now = datetime.now(timezone.utc)
    candidates: list[tuple[int, ShopAccount]] = []
    for acct in bubble_accounts():
        if remaining_today(acct) <= 0:
            continue
        if pending_hub_jobs_for(acct.id) >= MAX_PENDING_HUB_JOBS:
            continue
        wait = seconds_until_next_post(acct.id, now=now)
        if wait > 0:
            continue
        candidates.append((posts_today(acct.id), acct))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


def bubble_status_rows() -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for acct in bubble_accounts():
        pending_hub = pending_hub_jobs_for(acct.id)
        rows.append(
            {
                "account_id": acct.id,
                "slot": acct.phone_hub_slot,
                "sent_today": posts_today(acct.id),
                "limit": acct.daily_limit,
                "remaining": remaining_today(acct),
                "pending_hub_jobs": pending_hub,
                "wait_seconds": seconds_until_next_post(acct.id),
            }
        )
    return rows


def run_bubble_post_for_account(
    acct: ShopAccount,
    *,
    subject: str | None = None,
    preview: bool = False,
    force: bool = True,
) -> BubbleTickResult:
    """Generate slides, upload Zernio inbox draft, enqueue hub job."""
    if pending_hub_jobs_for(acct.id) >= MAX_PENDING_HUB_JOBS:
        detail = f"{pending_hub_jobs_for(acct.id)} pending hub job(s) — wait for phone finish"
        log_bubble_tick(account_id=acct.id, action="skipped", detail=detail)
        return BubbleTickResult(account_id=acct.id, action="skipped", detail=detail)

    subj = (subject or pick_bubble_subject(acct.id)).strip() or "frog"
    try:
        slides = generate_bubble_wrap_slides(
            subject=subj,
            account=acct.id,
            preview=preview,
            force=force,
        )
    except Exception as exc:  # noqa: BLE001 — scheduler must log and continue
        detail = f"slide generation failed: {exc}"
        log_bubble_tick(account_id=acct.id, action="failed", detail=detail)
        return BubbleTickResult(account_id=acct.id, action="failed", detail=detail, subject=subj)

    ok, msg, post_id = post_bubble_wrap_carousel(
        acct,
        slide1=slides.slide1,
        slide2=slides.slide2,
        title=f"{subj.title()} bubble wrap ASMR",
    )
    if not ok:
        detail = f"Zernio upload failed: {msg}"
        log_bubble_tick(account_id=acct.id, action="failed", detail=detail)
        log_post(
            account_id=acct.id,
            video_path=str(slides.slide1),
            caption=f"bubble:{subj}",
            ok=False,
            error=msg,
        )
        return BubbleTickResult(account_id=acct.id, action="failed", detail=detail, subject=subj)

    log_post(
        account_id=acct.id,
        video_path=str(slides.slide1),
        caption=f"bubble:{subj}",
        ok=True,
        publish_id=post_id,
    )

    hub_job_id = ""
    if acct.phone_hub_slot:
        job = enqueue_job(
            account_id=acct.id,
            phone_hub_slot=acct.phone_hub_slot,
            zernio_post_id=post_id,
            slide1=slides.slide1,
            slide2=slides.slide2,
            detail="inbox draft → Mackenzie on phone",
        )
        hub_job_id = job.id

    detail = f"{subj} → inbox draft post_id={post_id}"
    if hub_job_id:
        detail += f" hub_job={hub_job_id} → {acct.phone_hub_slot}"
    log_bubble_tick(account_id=acct.id, action="posted", detail=detail)
    return BubbleTickResult(
        account_id=acct.id,
        action="posted",
        detail=detail,
        subject=subj,
        post_id=post_id,
        hub_job_id=hub_job_id,
    )


def bubble_tick(
    *,
    account_id: str | None = None,
    confirm: bool = False,
    subject: str | None = None,
) -> BubbleTickResult:
    """One scheduler tick — picks account with quota; generates slides + inbox draft when confirmed."""
    acct = pick_bubble_account(account_id=account_id)
    if not acct:
        log_bubble_tick(account_id=account_id or "*", action="idle", detail="no eligible bubble account")
        return BubbleTickResult(account_id=account_id or "", action="idle", detail="quota/spacing/hub backlog")

    subj = (subject or pick_bubble_subject(acct.id)).strip() or "frog"
    if not confirm:
        detail = f"would post {subj} → {acct.phone_hub_slot} (add --confirm)"
        log_bubble_tick(account_id=acct.id, action="dry_run", detail=detail)
        return BubbleTickResult(
            account_id=acct.id,
            action="dry_run",
            detail=detail,
            subject=subj,
        )

    return run_bubble_post_for_account(acct, subject=subj)
