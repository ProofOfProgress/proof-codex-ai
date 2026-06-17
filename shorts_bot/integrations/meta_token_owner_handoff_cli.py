"""Owner handoff — click Generate Access Token on Graph API Explorer."""

from __future__ import annotations

import argparse
import re
import time

from rich.console import Console
from rich.panel import Panel

console = Console()

EXPLORER = "https://developers.facebook.com/tools/explorer/"

STEPS = """
[bold]App created — one more step on Desktop[/bold]

1. Click [bold cyan]Desktop[/bold cyan] tab in Cursor
2. Open tab: [bold]Graph API Explorer[/bold]
3. Right side → Meta App should say [bold cyan]Peripheral Bot[/bold cyan]
4. Click blue [bold]Generate Access Token[/bold]
5. If Facebook asks → click [bold]Continue as[/bold] (your name)
6. Come back here and say [bold]done[/bold]

[dim]We wait up to 5 minutes and auto-save the token.[/dim]
"""


def wait_for_token_and_save(*, wait_minutes: int = 5, page_name: str = "Peripheral Horror") -> str:
    import os

    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.profile_lock import clear_stale_profile_lock
    from shorts_bot.browser.stealth import launch_stealth_context
    from shorts_bot.integrations.meta_token_scrape import (
        resolve_page_token_from_user_token,
        setup_meta_page_api,
    )
    from shorts_bot.integrations.facebook_credentials import save_facebook_api_file

    clear_stale_profile_lock()
    console.print(Panel(STEPS, title="Get Facebook posting token", border_style="cyan"))

    headless = not bool(os.environ.get("DISPLAY"))
    user_token = ""
    with sync_playwright() as p:
        ctx = launch_stealth_context(p, headless=headless)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(EXPLORER, wait_until="domcontentloaded", timeout=120000)
        time.sleep(6)

        # Nudge Generate button for owner
        try:
            page.get_by_role("button", name=re.compile("Generate Access Token", re.I)).first.click(
                force=True, timeout=5000
            )
        except Exception:
            pass

        deadline = time.time() + wait_minutes * 60
        while time.time() < deadline:
            for label in ("Continue as", "Continue", "OK", "Done"):
                try:
                    btn = page.get_by_role("button", name=re.compile(label, re.I))
                    if btn.count():
                        btn.first.click(force=True, timeout=3000)
                        time.sleep(2)
                except Exception:
                    pass
            for sel in (
                'input[placeholder*="Access Token" i]',
                'input[aria-label*="Access Token" i]',
            ):
                loc = page.locator(sel)
                for i in range(min(loc.count(), 5)):
                    try:
                        val = (loc.nth(i).input_value() or "").strip()
                        if val.startswith("EAA") and len(val) > 40:
                            user_token = val
                            break
                    except Exception:
                        pass
                if user_token:
                    break
            if user_token:
                console.print("[green]Token detected — saving…[/green]")
                break
            remaining = int((deadline - time.time()) / 60)
            console.print(f"[dim]Waiting for Generate Access Token on Desktop… (~{remaining} min)[/dim]")
            time.sleep(10)

        page.screenshot(path="data/production/_meta_token_handoff.png", full_page=True)
        ctx.close()

    if not user_token:
        return (
            "No token yet. On Desktop: Graph API Explorer → Generate Access Token → "
            "Continue as you → say done again."
        )

    page_id, page_token, name = resolve_page_token_from_user_token(
        user_token, preferred_name=page_name
    )
    path = save_facebook_api_file(
        page_id=page_id,
        page_access_token=page_token,
        page_name=name,
    )
    return f"Saved Page token → {path} ({name}, id={page_id})"


def main() -> None:
    parser = argparse.ArgumentParser(description="Meta token owner handoff")
    parser.add_argument("--minutes", type=int, default=5)
    args = parser.parse_args()
    msg = wait_for_token_and_save(wait_minutes=args.minutes)
    console.print(msg)

    from shorts_bot.integrations.api_setup_cli import print_api_matrix

    console.print("")
    print_api_matrix()


if __name__ == "__main__":
    main()
