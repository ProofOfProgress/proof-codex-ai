"""Open browser tabs for remaining human logins (Desktop pane)."""

from __future__ import annotations

import argparse
import time

from rich.console import Console

from shorts_bot.browser.session import _SITE_URLS
from shorts_bot.browser.stealth import launch_stealth_context
from shorts_bot.config import settings

console = Console()

SITES = {
    "google": ("Google sign-in", _SITE_URLS["google"]),
    "youtube": ("YouTube Studio", _SITE_URLS["youtube"]),
    "turboscribe": ("TurboScribe", _SITE_URLS["turboscribe"]),
    "vidiq": ("vidIQ keyword research", _SITE_URLS["vidiq"]),
    "trends": ("Google Trends", _SITE_URLS["trends"]),
    "capcut": ("CapCut web", _SITE_URLS["capcut"]),
    "mixamo": ("Mixamo (Adobe login)", _SITE_URLS["mixamo"]),
    "recraft": ("Recraft profile (API key)", _SITE_URLS["recraft"]),
    "recraft_studio": ("Recraft Studio (style ID)", _SITE_URLS["recraft_studio"]),
}


def open_sites(keys: list[str], *, wait_minutes: int = 15) -> None:
    from playwright.sync_api import sync_playwright

    urls = [SITES[k][1] for k in keys if k in SITES]
    labels = [SITES[k][0] for k in keys if k in SITES]

    if any(k in keys for k in ("google", "youtube")):
        console.print(
            "[bold yellow]YouTube uploads use API OAuth — NOT this browser.[/bold yellow]\n"
            "Run: [cyan]python3 -m shorts_bot.youtube.auth_cli connect[/cyan]\n"
            "(Opens trusted Chrome for Google — Playwright often gets 'browser not secure'.)\n"
            "Phone/home PC: [cyan]python3 -m shorts_bot.youtube.auth_cli url[/cyan]\n"
        )
    console.print(
        "[bold green]Opening browser on your Desktop...[/bold green]\n"
        f"Sites: {', '.join(labels)}\n"
        "[yellow]In Cursor: click the Desktop tab.[/yellow]\n"
        "[dim]Google may block bot browsers — use auth_cli for YouTube API upload instead.[/dim]\n"
        f"Window stays open {wait_minutes} minutes.\n"
    )

    with sync_playwright() as p:
        context = launch_stealth_context(p, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        for i, url in enumerate(urls):
            if i == 0:
                page.goto(url, wait_until="domcontentloaded", timeout=120000)
            else:
                new_page = context.new_page()
                new_page.goto(url, wait_until="domcontentloaded", timeout=120000)
            console.print(f"[cyan]Tab {i + 1}:[/cyan] {url}")
        console.print("[bold]Sign in on each tab, then leave this running.[/bold]")
        time.sleep(wait_minutes * 60)
        context.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Open login pages in saved browser profile.")
    parser.add_argument(
        "--only",
        choices=list(SITES.keys()),
        action="append",
        help="Open specific site(s) only",
    )
    parser.add_argument("--minutes", type=int, default=15, help="How long to keep browser open")
    parser.add_argument(
        "--all-remaining",
        action="store_true",
        help="Open Google + YouTube Studio for channel login",
    )
    args = parser.parse_args()

    if args.only:
        keys = args.only
    elif args.all_remaining:
        keys = ["google", "youtube"]
    else:
        keys = ["google", "youtube"]

    open_sites(keys, wait_minutes=args.minutes)


if __name__ == "__main__":
    main()
