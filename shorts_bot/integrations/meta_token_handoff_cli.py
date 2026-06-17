"""Open Meta Graph API Explorer to copy Page ID + Page access token."""

from __future__ import annotations

import argparse
import time

from rich.console import Console

console = Console()

EXPLORER = "https://developers.facebook.com/tools/explorer/"
REGISTER = "https://developers.facebook.com/async/registration/"
DOCS = "https://developers.facebook.com/docs/graph-api/reference/page/video_reels/"


def open_meta_token_handoff(*, wait_minutes: int = 15) -> None:
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    console.print(
        "[bold]Meta token handoff[/bold]\n\n"
        "1. Register as Facebook Developer (one-time): open Register link below\n"
        "2. Graph API Explorer → select your app + **Peripheral Horror** Page\n"
        "2. Permissions: `pages_manage_posts`, `pages_show_list`, `pages_read_engagement`\n"
        "3. Generate token → copy **Page access token**\n"
        "4. GET `me/accounts` or your Page → copy **Page ID**\n"
        "5. Add to Cursor Secrets:\n"
        "   FACEBOOK_PAGE_ID=61590716288819  (Peripheral Horror — already created)\n"
        "   META_PAGE_ACCESS_TOKEN=...\n"
        "6. Run: bash scripts/install.sh\n\n"
        f"Explorer: {EXPLORER}\n"
    )

    with sync_playwright() as p:
        ctx = launch_stealth_context(p, headless=False)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(EXPLORER, wait_until="domcontentloaded", timeout=120000)
        new = ctx.new_page()
        new.goto(DOCS, wait_until="domcontentloaded", timeout=120000)
        time.sleep(wait_minutes * 60)
        ctx.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Meta Page token handoff")
    parser.add_argument("--open-browser", action="store_true")
    parser.add_argument("--minutes", type=int, default=15)
    args = parser.parse_args()
    if args.open_browser:
        open_meta_token_handoff(wait_minutes=args.minutes)
    else:
        from shorts_bot.integrations.facebook_page_discover import discover_managed_pages
        from shorts_bot.integrations.facebook_reel_api import probe_facebook_reel_api

        ok, msg = probe_facebook_reel_api()
        console.print(("OK" if ok else "FIX") + " " + msg)
        pages, page_msg = discover_managed_pages(timeout_sec=20)
        if pages:
            for p in pages:
                console.print(f"Page: [cyan]{p.name}[/cyan] id={p.page_id}")
        else:
            console.print(page_msg)
        if not ok:
            console.print("Run: python3 -m shorts_bot.integrations.meta_token_handoff_cli --open-browser")
            console.print("Add FACEBOOK_PAGE_ID + META_PAGE_ACCESS_TOKEN to Cursor Secrets → bash scripts/install.sh")


if __name__ == "__main__":
    main()
