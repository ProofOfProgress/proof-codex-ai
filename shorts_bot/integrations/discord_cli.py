"""CLI — read-only Discord sync into course inbox."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

from shorts_bot.integrations.discord_read import discord_setup_status, sync_discord_inbox

console = Console()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only Discord sync — never sends messages"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Show Discord bot setup status")

    sync_p = sub.add_parser("sync", help="Fetch allowlisted channels → course inbox")
    sync_p.add_argument("--limit", type=int, default=50, help="Messages per channel (max 100)")

    args = parser.parse_args(argv)

    if args.cmd == "status":
        console.print(str(discord_setup_status()))
        return 0

    if args.cmd == "sync":
        try:
            path = sync_discord_inbox(limit_per_channel=args.limit)
        except RuntimeError as exc:
            console.print(f"[red]FAIL[/red] {exc}")
            return 1
        console.print(f"[green]OK[/green] wrote {path}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
