"""Zernio connection status."""

from __future__ import annotations

import argparse
import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from shorts_bot.zernio.client import credentials_configured, list_accounts

console = Console()


def status_dict() -> dict:
    if not credentials_configured():
        return {
            "configured": False,
            "accounts": [],
            "tiktok_ready": False,
            "facebook_ready": False,
        }
    accounts = []
    tiktok = facebook = False
    for acct in list_accounts():
        plat = (acct.get("platform") or "").lower()
        aid = acct.get("_id") or acct.get("id")
        name = acct.get("displayName") or acct.get("username") or plat
        active = acct.get("isActive", True) and acct.get("enabled", True)
        accounts.append({"platform": plat, "id": aid, "name": name, "active": active})
        if plat == "tiktok" and active:
            tiktok = True
        if plat == "facebook" and active:
            facebook = True
    return {
        "configured": True,
        "accounts": accounts,
        "tiktok_ready": tiktok,
        "facebook_ready": facebook,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Zernio multi-platform upload status")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    st = status_dict()
    if args.json:
        print(json.dumps(st, indent=2))
        return

    if not st["configured"]:
        console.print(Panel("Add ZERNIO_API_KEY to Cursor Secrets or .env", title="Zernio"))
        return

    table = Table(title="Zernio connected accounts")
    table.add_column("Platform")
    table.add_column("Name")
    table.add_column("Account ID")
    table.add_column("Active")
    for acct in st["accounts"]:
        table.add_row(
            acct["platform"],
            acct["name"],
            str(acct["id"]),
            "yes" if acct["active"] else "no",
        )
    console.print(table)
    console.print(f"TikTok ready: {st['tiktok_ready']}")
    console.print(f"Facebook ready: {st['facebook_ready']}")


if __name__ == "__main__":
    main()
