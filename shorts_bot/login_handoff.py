"""Open browser tabs for remaining human logins (Desktop pane)."""

from __future__ import annotations

import argparse
import time

from rich.console import Console

from shorts_bot.browser.session import _SITE_URLS
from shorts_bot.config import settings

console = Console()

SITES = {
    "google": ("Google sign-in", _SITE_URLS["google"]),
    "youtube": ("YouTube Studio", _SITE_URLS["youtube"]),
    "turboscribe": ("TurboScribe", _SITE_URLS["turboscribe"]),
    "vidiq": ("vidIQ keyword research", _SITE_URLS["vidiq"]),
    "trends": ("Google Trends", _SITE_URLS["trends"]),
    "capcut": ("CapCut web", _SITE_URLS["capcut"]),
    "discord": ("Discord app", _SITE_URLS["discord"]),
}


def open_sites(keys: list[str], *, wait_minutes: int = 15) -> None:
    from playwright.sync_api import sync_playwright

    urls = [SITES[k][1] for k in keys if k in SITES]
    labels = [SITES[k][0] for k in keys if k in SITES]

    console.print(
        "[bold green]Opening browser on your Desktop...[/bold green]\n"
        f"Sites: {', '.join(labels)}\n"
        "[yellow]In Cursor: click the Desktop tab to sign in.[/yellow]\n"
        f"Window stays open {wait_minutes} minutes.\n"
    )

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(settings.browser_profile_dir),
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        )
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
        help="Open TurboScribe + CapCut (optional human steps)",
    )
    args = parser.parse_args()

    if args.only:
        keys = args.only
    elif args.all_remaining:
        keys = ["turboscribe", "capcut"]
    else:
        keys = ["youtube", "turboscribe", "capcut"]

    open_sites(keys, wait_minutes=args.minutes)


if __name__ == "__main__":
    main()
