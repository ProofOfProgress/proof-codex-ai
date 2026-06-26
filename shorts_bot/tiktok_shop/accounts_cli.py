"""Scaffold and validate data/tiktok_shop/accounts.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


def _bubble_template(count: int = 3) -> dict:
    limits = [10, 1, 5, 8, 3]
    rows = []
    for i in range(1, count + 1):
        rows.append(
            {
                "id": f"bubble_{i}",
                "label": f"Bubble account {i}",
                "track": "bubble",
                "daily_limit": limits[(i - 1) % len(limits)],
                "enabled": True,
                "post_via": "zernio",
                "zernio_account_id": "",
            }
        )
    return {"accounts": rows}


def scaffold_accounts(*, track: str = "bubble", count: int = 3, force: bool = False) -> Path:
    from shorts_bot.tiktok_shop.accounts import accounts_config_path

    path = accounts_config_path()
    if path.is_file() and not force:
        raise FileExistsError(f"{path} already exists — use --force to overwrite")

    if track == "bubble":
        data = _bubble_template(count)
    else:
        data = {
            "accounts": [
                {
                    "id": f"shop_{i}",
                    "label": f"Affiliate account {i}",
                    "track": "affiliate",
                    "daily_limit": 8,
                    "enabled": True,
                    "post_via": "zernio",
                    "zernio_account_id": "",
                }
                for i in range(1, count + 1)
            ]
        }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def validate_accounts() -> list[str]:
    from shorts_bot.tiktok_shop.accounts import accounts_config_path, load_accounts

    issues: list[str] = []
    path = accounts_config_path()
    if not path.is_file():
        issues.append(f"Missing {path} — run: python3 -m shorts_bot.tiktok_shop.accounts_cli scaffold")
        return issues

    for acct in load_accounts():
        if acct.post_via == "zernio" and not (acct.zernio_account_id or "").strip():
            issues.append(f"{acct.id}: post_via=zernio but zernio_account_id is empty")
        if acct.post_via == "tiktok_api":
            token = acct.resolved_token_path()
            if not token or not token.is_file():
                issues.append(f"{acct.id}: tiktok_api but no token at {token}")
    return issues


def sync_zernio_snippet() -> str:
    from shorts_bot.zernio.client import credentials_configured, list_accounts

    if not credentials_configured():
        raise RuntimeError("ZERNIO_API_KEY not configured")

    rows = []
    for acct in list_accounts():
        if (acct.get("platform") or "").lower() != "tiktok":
            continue
        if acct.get("isActive") is False or acct.get("enabled") is False:
            continue
        aid = (acct.get("_id") or acct.get("id") or "").strip()
        name = acct.get("username") or acct.get("name") or aid
        if aid:
            rows.append({"zernio_account_id": aid, "label": name, "platform": "tiktok"})

    return json.dumps({"zernio_tiktok_accounts": rows}, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok Shop accounts.json helpers")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sc = sub.add_parser("scaffold", help="Create accounts.json template")
    sc.add_argument("--track", choices=["bubble", "affiliate"], default="bubble")
    sc.add_argument("--count", type=int, default=3)
    sc.add_argument("--force", action="store_true")

    sub.add_parser("validate", help="Check accounts.json wiring")
    sub.add_parser("sync-zernio", help="Print Zernio TikTok account ids to paste")

    args = parser.parse_args()

    if args.cmd == "scaffold":
        path = scaffold_accounts(track=args.track, count=args.count, force=args.force)
        console.print(f"[green]Wrote[/green] {path}")
        console.print("[dim]Paste zernio_account_id values — run sync-zernio for ids[/dim]")
        return

    if args.cmd == "validate":
        issues = validate_accounts()
        if not issues:
            console.print("[green]accounts.json OK[/green]")
            raise SystemExit(0)
        for issue in issues:
            console.print(f"[red]• {issue}[/red]")
        raise SystemExit(1)

    console.print(sync_zernio_snippet())


if __name__ == "__main__":
    main()
