"""Affiliate post scheduler — run from cron on an always-on machine (not Cursor automations)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.accounts import ShopAccount, load_account
from shorts_bot.tiktok_shop.poster import post_clip
from shorts_bot.tiktok_shop.queue import load_queue, pending_posts, save_queue
from shorts_bot.tiktok_shop.quota import posts_today, remaining_today


def min_post_interval_seconds() -> int:
    minutes = int(getattr(settings, "tiktok_shop_min_post_interval_minutes", 30) or 30)
    return max(1, minutes) * 60


def scheduler_log_path() -> Path:
    return settings.data_dir / "tiktok_shop" / "scheduler_log.jsonl"


def _log_path() -> Path:
    return settings.data_dir / "tiktok_shop" / "post_log.jsonl"


def last_successful_post_at(account_id: str) -> datetime | None:
    path = _log_path()
    if not path.is_file():
        return None
    latest: datetime | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("account_id") != account_id or not row.get("ok"):
            continue
        raw = str(row.get("at") or "")
        try:
            ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if latest is None or ts > latest:
            latest = ts
    return latest


def seconds_until_next_post(account_id: str, *, now: datetime | None = None) -> int:
    now = now or datetime.now(timezone.utc)
    last = last_successful_post_at(account_id)
    if last is None:
        return 0
    elapsed = (now - last).total_seconds()
    wait = min_post_interval_seconds() - elapsed
    return max(0, int(wait))


def log_scheduler_tick(*, account_id: str, action: str, detail: str = "") -> None:
    path = scheduler_log_path()
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
class TickResult:
    ok: bool
    action: str
    message: str
    account_id: str = ""
    video_path: str = ""
    publish_id: str = ""


def resolve_account(account_id: str) -> ShopAccount | None:
    return load_account(account_id)


def tick_post(*, account_id: str = "affiliate_main", confirm: bool = False) -> TickResult:
    """
    Post the next queued clip if spacing + quota allow.
    Safe to call every 30 minutes from cron — no-ops when not due.
    """
    account = resolve_account(account_id)
    if account is None:
        msg = f"Unknown account {account_id!r} — check data/tiktok_shop/accounts.json"
        log_scheduler_tick(account_id=account_id, action="error", detail=msg)
        return TickResult(ok=False, action="error", message=msg, account_id=account_id)

    if not account.enabled:
        msg = f"{account.id} is disabled — enable after Zernio hookup"
        log_scheduler_tick(account_id=account.id, action="skipped", detail=msg)
        return TickResult(ok=True, action="skipped", message=msg, account_id=account.id)

    wait = seconds_until_next_post(account.id)
    if wait > 0:
        mins = max(1, wait // 60)
        msg = f"Spacing — wait ~{mins}m before next post on {account.id}"
        log_scheduler_tick(account_id=account.id, action="skipped", detail=msg)
        return TickResult(ok=True, action="skipped", message=msg, account_id=account.id)

    if remaining_today(account) <= 0:
        msg = f"{account.id} at daily cap ({account.daily_limit}/day)"
        log_scheduler_tick(account_id=account.id, action="skipped", detail=msg)
        return TickResult(ok=True, action="skipped", message=msg, account_id=account.id)

    pending = pending_posts(account_id=account.id)
    if not pending:
        pending = pending_posts()
    if not pending:
        msg = "Queue empty — enqueue QC-pass clips first"
        log_scheduler_tick(account_id=account.id, action="skipped", detail=msg)
        return TickResult(ok=True, action="skipped", message=msg, account_id=account.id)

    rows = load_queue()
    pending_idx = next(
        (
            i
            for i, r in enumerate(rows)
            if r.get("status") == "pending"
            and (not r.get("account_id") or r.get("account_id") == account.id)
        ),
        None,
    )
    if pending_idx is None:
        pending_idx = next((i for i, r in enumerate(rows) if r.get("status") == "pending"), None)
    if pending_idx is None:
        msg = "No pending queue row matched"
        log_scheduler_tick(account_id=account.id, action="skipped", detail=msg)
        return TickResult(ok=True, action="skipped", message=msg, account_id=account.id)

    row = rows[pending_idx]
    video = Path(str(row.get("video_path") or ""))
    caption = str(row.get("caption") or "")
    product = str(row.get("product") or "")

    if not video.is_file():
        msg = f"Missing video: {video}"
        log_scheduler_tick(account_id=account.id, action="error", detail=msg)
        return TickResult(ok=False, action="error", message=msg, account_id=account.id)

    from shorts_bot.tiktok_shop.module1_qc import run_module1_qc

    qc = run_module1_qc(video, caption=caption, product=product, account_id=account.id)
    if not qc.passed:
        msg = f"QC blocked upload: {'; '.join(qc.violations[:3])}"
        log_scheduler_tick(account_id=account.id, action="blocked", detail=msg)
        return TickResult(ok=False, action="blocked", message=msg, account_id=account.id)

    if not confirm:
        msg = f"Ready to post {video.name} — dry run (add --confirm or cron uses it)"
        log_scheduler_tick(account_id=account.id, action="dry_run", detail=msg)
        return TickResult(
            ok=True,
            action="dry_run",
            message=msg,
            account_id=account.id,
            video_path=str(video),
        )

    ok, msg, pub = post_clip(account, video_path=video, caption=caption, product=product)
    if ok:
        rows[pending_idx]["status"] = "posted"
        rows[pending_idx]["account_id"] = account.id
        rows[pending_idx]["publish_id"] = pub
        save_queue(rows)
        log_scheduler_tick(account_id=account.id, action="posted", detail=f"{video.name} → {pub}")
        return TickResult(
            ok=True,
            action="posted",
            message=msg,
            account_id=account.id,
            video_path=str(video),
            publish_id=pub,
        )

    log_scheduler_tick(account_id=account.id, action="failed", detail=msg)
    return TickResult(
        ok=False,
        action="failed",
        message=msg,
        account_id=account.id,
        video_path=str(video),
    )


def scheduler_status(*, account_id: str = "affiliate_main") -> dict:
    account = resolve_account(account_id)
    last = last_successful_post_at(account_id) if account else None
    wait = seconds_until_next_post(account_id) if account else 0
    pending = pending_posts(account_id=account_id) if account else pending_posts()
    return {
        "account_id": account_id,
        "account_found": account is not None,
        "enabled": bool(account and account.enabled),
        "sent_today": posts_today(account_id) if account else 0,
        "daily_limit": account.daily_limit if account else 0,
        "remaining_today": remaining_today(account) if account else 0,
        "queue_pending": len(pending),
        "last_post_at": last.isoformat() if last else None,
        "seconds_until_next": wait,
        "min_interval_minutes": min_post_interval_seconds() // 60,
        "cron_script": "bash scripts/affiliate_cron.sh",
    }
