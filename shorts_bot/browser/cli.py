"""CLI: browse URLs and open visible browser sessions."""

from __future__ import annotations

import argparse

from rich.console import Console

from shorts_bot.browser.session import browse_url, is_playwright_ready, open_browser_for_human

console = Console()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Soft Continuity browser control")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Check Playwright + Chromium")

    browse_p = sub.add_parser("browse", help="Headless browse — extract page text")
    browse_p.add_argument("url", help="URL or site alias (vidiq, youtube, trends)")
    browse_p.add_argument("--screenshot", action="store_true")

    open_p = sub.add_parser("open", help="Visible browser for human control")
    open_p.add_argument("url", help="URL or site alias")
    open_p.add_argument("--minutes", type=int, default=15)
    open_p.add_argument("--block", action="store_true", help="Keep open until timeout")

    args = parser.parse_args(argv)

    if args.cmd == "status":
        ok, detail = is_playwright_ready()
        console.print(f"[green]ready[/green] {detail}" if ok else f"[red]not ready[/red] {detail}")
        return 0 if ok else 1

    if args.cmd == "browse":
        result = browse_url(args.url, screenshot=args.screenshot)
        console.print(result.summary())
        return 0

    if args.cmd == "open":
        result = open_browser_for_human(args.url, minutes=args.minutes, block=args.block)
        console.print(result.message or result.url)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
