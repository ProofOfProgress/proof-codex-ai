"""Load Shop factory accounts (3 × 10 posts/day default)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings


@dataclass(frozen=True)
class ShopAccount:
    id: str
    label: str
    daily_limit: int = 10
    enabled: bool = True
    tiktok_token_path: Path | None = None
    zernio_account_id: str | None = None
    post_via: str = "zernio"  # zernio | tiktok_api

    def resolved_token_path(self) -> Path | None:
        if self.tiktok_token_path:
            return self.tiktok_token_path
        return None


def accounts_config_path() -> Path:
    return settings.data_dir / "tiktok_shop" / "accounts.json"


def load_accounts() -> list[ShopAccount]:
    path = accounts_config_path()
    if not path.is_file():
        return _default_accounts()
    raw = json.loads(path.read_text(encoding="utf-8"))
    rows = raw.get("accounts") if isinstance(raw, dict) else raw
    if not isinstance(rows, list):
        return _default_accounts()
    out: list[ShopAccount] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        token = row.get("tiktok_token_path")
        out.append(
            ShopAccount(
                id=str(row.get("id") or "").strip(),
                label=str(row.get("label") or row.get("id") or "").strip(),
                daily_limit=max(1, int(row.get("daily_limit") or 10)),
                enabled=bool(row.get("enabled", True)),
                tiktok_token_path=Path(token) if token else None,
                zernio_account_id=(row.get("zernio_account_id") or None),
                post_via=str(row.get("post_via") or "zernio").strip().lower(),
            )
        )
    return [a for a in out if a.id and a.enabled]


def _default_accounts() -> list[ShopAccount]:
    base = settings.data_dir / "tiktok_shop" / "tokens"
    return [
        ShopAccount(id="shop_1", label="Shop account 1", tiktok_token_path=base / "shop_1.json"),
        ShopAccount(id="shop_2", label="Shop account 2", tiktok_token_path=base / "shop_2.json"),
        ShopAccount(id="shop_3", label="Shop account 3", tiktok_token_path=base / "shop_3.json"),
    ]


def total_daily_cap(accounts: list[ShopAccount] | None = None) -> int:
    accts = accounts or load_accounts()
    return sum(a.daily_limit for a in accts)
