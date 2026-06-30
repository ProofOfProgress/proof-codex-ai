"""CLI — hub browser intel sync (Discord web + course pages)."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

from shorts_bot.integrations.hub_browser_intel import intel_targets, sync_hub_browser_inbox

console = Console()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hub browser read-only intel sync")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="List configured intel URLs")

    sync_p = sub.add_parser("sync", help="Browse allowlisted pages → course inbox")
    sync_p.add_argument("--screenshot", action="store_true")

    args = parser.parse_args(argv)

    if args.cmd == "status":
        targets = intel_targets()
        if not targets:
            console.print("[yellow]No URLs configured[/yellow] — set COURSE_* and DISCORD_* env vars")
            return 1
        for name, url in targets:
            console.print(f"  {name}: {url}")
        return 0

    if args.cmd == "sync":
        try:
            path = sync_hub_browser_inbox(screenshot=args.screenshot)
        except RuntimeError as exc:
            console.print(f"[red]FAIL[/red] {exc}")
            return 1
        console.print(f"[green]OK[/green] wrote {path}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
