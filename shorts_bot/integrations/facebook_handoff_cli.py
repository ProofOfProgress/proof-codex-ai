"""Facebook / Meta Page setup — browser handoff for Reels distribution."""

from __future__ import annotations

import argparse
import time

from rich.console import Console

console = Console()

FACEBOOK_URL = "https://www.facebook.com/"
FACEBOOK_SIGNUP_URL = "https://www.facebook.com/r.php"
CREATE_PAGE_URL = "https://www.facebook.com/pages/create"
BUSINESS_SUITE_URL = "https://business.facebook.com/latest/home"


def facebook_status() -> tuple[bool, list[str]]:
    from pathlib import Path

    lines: list[str] = []
    profile = Path("data/browser_profile")
    has_profile = profile.exists() and any(profile.iterdir())
    lines.append(
        f"Browser profile: {'OK' if has_profile else 'missing'} (data/browser_profile/)"
    )
    lines.append("Facebook API posting: not wired yet — manual Reels upload from Page")
    lines.append("Docs: docs/FOR_OWNER_FACEBOOK_SETUP.md")
    ready = has_profile
    return ready, lines


def open_facebook_browser(*, wait_minutes: int = 25) -> None:
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    console.print(
        "[bold green]Opening Facebook setup in your Desktop browser…[/bold green]\n"
        "[yellow]In Cursor: click the Desktop tab.[/yellow]\n\n"
        "[bold]Do these in order:[/bold]\n"
        "1. Sign up or log in to Facebook (personal account).\n"
        "2. Create a Page named [cyan]Peripheral[/cyan] (Entertainment).\n"
        "3. Open Business Suite tab — optional, for scheduling Reels.\n"
        "4. When done, upload Shorts from Page → Create → Reel.\n"
        f"\nWindow stays open {wait_minutes} minutes.\n"
        "Full checklist: docs/FOR_OWNER_FACEBOOK_SETUP.md\n"
    )

    urls = [
        (FACEBOOK_SIGNUP_URL, "Sign up / log in"),
        (CREATE_PAGE_URL, "Create Page"),
        (BUSINESS_SUITE_URL, "Meta Business Suite"),
    ]

    with sync_playwright() as p:
        context = launch_stealth_context(p, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        for i, (url, label) in enumerate(urls):
            if i == 0:
                page.goto(url, wait_until="domcontentloaded", timeout=120000)
            else:
                new_page = context.new_page()
                new_page.goto(url, wait_until="domcontentloaded", timeout=120000)
            console.print(f"[cyan]Tab {i + 1} ({label}):[/cyan] {url}")
        console.print("[bold]Complete signup + Page creation, then leave this running.[/bold]")
        time.sleep(wait_minutes * 60)
        context.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Facebook Page + Reels setup handoff")
    parser.add_argument("--open-browser", action="store_true", help="Open Facebook tabs in Desktop browser")
    parser.add_argument("--status", action="store_true", help="Print setup status")
    parser.add_argument("--minutes", type=int, default=25, help="Browser stay-open time")
    args = parser.parse_args()

    if args.open_browser:
        open_facebook_browser(wait_minutes=args.minutes)
        raise SystemExit(0)

    ready, lines = facebook_status()
    for line in lines:
        console.print(line)
    if not args.status:
        console.print(
            "\nRun: [cyan]python3 -m shorts_bot.integrations.facebook_handoff_cli --open-browser[/cyan]"
        )
    raise SystemExit(0 if ready else 1)


if __name__ == "__main__":
    main()
