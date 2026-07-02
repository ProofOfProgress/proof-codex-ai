"""CLI: browse URLs and open visible browser sessions."""

from __future__ import annotations

import argparse

from rich.console import Console

from shorts_bot.browser.session import browse_url, is_playwright_ready, open_browser_for_human

console = Console()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Don't Blink browser control")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Check Playwright + Chromium")

    browse_p = sub.add_parser("browse", help="Headless browse — extract page text")
    browse_p.add_argument("url", help="URL or site alias (vidiq, youtube, trends)")
    browse_p.add_argument("--screenshot", action="store_true")

    open_p = sub.add_parser("open", help="Visible browser for human control")
    open_p.add_argument("url", help="URL or site alias")
    open_p.add_argument("--minutes", type=int, default=15)
    open_p.add_argument("--block", action="store_true", help="Keep open until timeout")

    crawl_course_p = sub.add_parser(
        "crawl-course",
        help="Crawl Momentum Academy (Playwright DOM, read-only)",
    )
    crawl_course_p.add_argument("--max-pages", type=int, default=25)
    crawl_course_p.add_argument(
        "--deep",
        action="store_true",
        help="BFS deep crawl (up to 100 pages)",
    )

    crawl_discord_p = sub.add_parser(
        "crawl-discord",
        help="Read-only Discord web scrape (hub profile)",
    )

    login_discord_p = sub.add_parser(
        "login-discord",
        help="Log into Discord web (saves cookies in profile)",
    )
    login_discord_p.add_argument(
        "--visible",
        action="store_true",
        help="Show browser window (hub desktop only)",
    )

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

    if args.cmd == "crawl-course":
        if args.deep:
            from shorts_bot.browser.course_deep_crawl import deep_crawl_momentum

            path = deep_crawl_momentum(max_pages=max(args.max_pages, 100))
        else:
            from shorts_bot.browser.course_session import crawl_course_site

            path = crawl_course_site(max_pages=args.max_pages)
        console.print(f"[green]Wrote[/green] {path}")
        return 0

    if args.cmd == "crawl-discord":
        from shorts_bot.browser.discord_session import crawl_discord

        path = crawl_discord()
        console.print(f"[green]Wrote[/green] {path}")
        return 0

    if args.cmd == "login-discord":
        from shorts_bot.browser.discord_session import login_discord_session

        profile = login_discord_session(headless=not args.visible)
        console.print(f"[green]Discord session saved[/green] → {profile}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
