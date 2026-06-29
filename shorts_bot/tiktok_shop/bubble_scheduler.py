"""Bubble wrap scheduler — Zernio inbox draft + hub job queue (phones finish Mackenzie)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from shorts_bot.config import settings
from shorts_bot.phone_hub.jobs import list_jobs
from shorts_bot.tiktok_shop.accounts import ShopAccount, bubble_accounts, load_account
from shorts_bot.tiktok_shop.quota import posts_today, remaining_today
from shorts_bot.tiktok_shop.scheduler import min_post_interval_seconds, seconds_until_next_post


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


def pick_bubble_account(*, account_id: str | None = None) -> ShopAccount | None:
    if account_id:
        acct = load_account(account_id)
        return acct if acct and acct.track.startswith("bubble") and acct.enabled else None
    now = datetime.now(timezone.utc)
    candidates: list[tuple[int, ShopAccount]] = []
    for acct in bubble_accounts():
        if remaining_today(acct.id, acct.daily_limit) <= 0:
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
        pending_hub = sum(
            1 for j in list_jobs(status="pending") if j.account_id == acct.id
        )
        rows.append(
            {
                "account_id": acct.id,
                "slot": acct.phone_hub_slot,
                "sent_today": posts_today(acct.id),
                "limit": acct.daily_limit,
                "remaining": remaining_today(acct.id, acct.daily_limit),
                "pending_hub_jobs": pending_hub,
                "wait_seconds": seconds_until_next_post(acct.id),
            }
        )
    return rows


def bubble_tick(
    *,
    account_id: str | None = None,
    confirm: bool = False,
) -> BubbleTickResult:
    """One scheduler tick — picks account with quota; full auto-post when slides pipeline wired."""
    acct = pick_bubble_account(account_id=account_id)
    if not acct:
        log_bubble_tick(account_id=account_id or "*", action="idle", detail="no eligible bubble account")
        return BubbleTickResult(account_id=account_id or "", action="idle", detail="quota/spacing")

    if not confirm:
        log_bubble_tick(
            account_id=acct.id,
            action="dry_run",
            detail=f"would post to {acct.phone_hub_slot}",
        )
        return BubbleTickResult(
            account_id=acct.id,
            action="dry_run",
            detail=f"add --confirm; slides not auto-generated in tick yet",
        )

    log_bubble_tick(account_id=acct.id, action="skipped", detail="generate slides + post-carousel separately")
    return BubbleTickResult(
        account_id=acct.id,
        action="skipped",
        detail="Use: factory_cli bubble-slides → post-carousel --confirm --enqueue-hub",
    )
