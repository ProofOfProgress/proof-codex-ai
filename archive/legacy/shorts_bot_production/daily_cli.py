"""Daily autopilot — InVideo backend only."""

from __future__ import annotations

import argparse

from rich.console import Console

from shorts_bot.production.invideo_daily import run_invideo_daily

console = Console()


def run_daily(*, topic: str | None = None, upload: bool | None = None) -> str:
    result = run_invideo_daily(topic=topic, upload=upload)
    return result.summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one full daily Short via InVideo.")
    parser.add_argument("--topic", default=None, help="Override rotated topic")
    parser.add_argument("--no-upload", action="store_true")
    args = parser.parse_args()
    upload = False if args.no_upload else None
    console.print(f"[green]{run_daily(topic=args.topic, upload=upload)}[/green]")


if __name__ == "__main__":
    main()
