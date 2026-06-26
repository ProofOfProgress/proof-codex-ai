"""Daily post quota per Shop account."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.accounts import ShopAccount, load_accounts


def _log_path() -> Path:
    return settings.data_dir / "tiktok_shop" / "post_log.jsonl"


def posts_today(account_id: str) -> int:
    path = _log_path()
    if not path.is_file():
        return 0
    today = datetime.now(timezone.utc).date().isoformat()
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not str(row.get("at", "")).startswith(today):
            continue
        if row.get("account_id") == account_id and row.get("ok"):
            count += 1
    return count


def remaining_today(account: ShopAccount) -> int:
    return max(0, account.daily_limit - posts_today(account.id))


def pick_account_for_post(accounts: list[ShopAccount] | None = None) -> ShopAccount | None:
    """Account with the most remaining quota today (spread load evenly)."""
    accts = accounts or load_accounts()
    if not accts:
        return None
    ranked = sorted(accts, key=lambda a: remaining_today(a), reverse=True)
    best = ranked[0]
    if remaining_today(best) <= 0:
        return None
    return best


def log_post(
    *,
    account_id: str,
    video_path: str,
    caption: str,
    product: str = "",
    ok: bool,
    error: str = "",
    publish_id: str = "",
) -> None:
    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "at": datetime.now(timezone.utc).isoformat(),
        "account_id": account_id,
        "video": video_path,
        "caption": caption[:300],
        "product": product,
        "ok": ok,
        "error": error[:300],
        "publish_id": publish_id,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def status_rows() -> list[dict]:
    rows = []
    for acct in load_accounts():
        sent = posts_today(acct.id)
        rows.append({
            "id": acct.id,
            "label": acct.label,
            "sent_today": sent,
            "limit": acct.daily_limit,
            "remaining": max(0, acct.daily_limit - sent),
            "post_via": acct.post_via,
        })
    return rows
