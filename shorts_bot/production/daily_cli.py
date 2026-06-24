"""Daily autopilot — InVideo backend only."""

from __future__ import annotations

import argparse

from rich.console import Console

from shorts_bot.production.invideo_daily import run_invideo_daily

console = Console()


def run_daily(
    *,
    topic: str | None = None,
    upload: bool | None = None,
    wait_render_sec: int = 2400,
) -> str:
    result = run_invideo_daily(topic=topic, upload=upload, wait_render_sec=wait_render_sec)
    return result.summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one full daily Short via InVideo.")
    parser.add_argument("--topic", default=None, help="Override rotated topic")
    parser.add_argument("--upload", action="store_true", help="Upload after render")
    parser.add_argument("--no-upload", action="store_true")
    parser.add_argument(
        "--wait-render-sec",
        type=int,
        default=2400,
        help="Max seconds to wait for InVideo render (default 40 min)",
    )
    args = parser.parse_args()
    upload = True if args.upload else (False if args.no_upload else None)
    console.print(
        f"[green]{run_daily(topic=args.topic, upload=upload, wait_render_sec=args.wait_render_sec)}[/green]"
    )


if __name__ == "__main__":
    main()
