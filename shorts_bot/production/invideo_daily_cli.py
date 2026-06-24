"""CLI — one command daily Short via InVideo."""

from __future__ import annotations

import argparse

from rich.console import Console

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Daily TikTok Shop gadget Short: InVideo → MP4 → upload"
    )
    parser.add_argument("--topic", default=None, help="Override product topic")
    parser.add_argument("--no-upload", action="store_true")
    parser.add_argument(
        "--wait-render-sec",
        type=int,
        default=2400,
        help="Max seconds to wait for InVideo render (default 40 min)",
    )
    args = parser.parse_args()

    from shorts_bot.production.invideo_daily import run_invideo_daily

    result = run_invideo_daily(
        topic=args.topic,
        upload=False if args.no_upload else None,
        wait_render_sec=args.wait_render_sec,
    )
    if result.ok:
        console.print(f"[green]{result.summary}[/green]")
    else:
        console.print(f"[yellow]{result.summary}[/yellow]")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
