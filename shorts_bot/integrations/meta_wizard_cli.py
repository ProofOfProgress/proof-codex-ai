"""Walk owner through Meta app create — correct steps (no password until Create app)."""

from __future__ import annotations

import argparse
import re
import time

from rich.console import Console
from rich.panel import Panel

console = Console()

APP_CREATE = "https://developers.facebook.com/apps/create/"
MY_APPS = "https://developers.facebook.com/apps/"

OWNER_STEPS = """
[bold]You were right — no password yet.[/bold] The app does not exist yet.

On [bold cyan]Desktop → Chrome[/bold cyan], do this on the [bold]Create an app[/bold] tab:

[bold]1.[/bold] Click the circle next to [bold]Business[/bold] (briefcase icon)
[bold]2.[/bold] Click [bold]Next[/bold] (bottom right)
[bold]3.[/bold] In the middle of the page, type app name: [bold cyan]Peripheral Bot[/bold]
     [dim](NOT the search bar at the very top)[/dim]
[bold]4.[/bold] Click green [bold]Create app[/bold]

[dim]Only after step 4, Facebook might ask for your password once.
If it does, type it then. If not, you're done.[/dim]

[bold]Or[/bold] on the [bold]My apps[/bold] tab: click green [bold]Create App[/bold] — same wizard.
"""


def try_create_app_in_browser(*, app_name: str = "Peripheral Bot") -> tuple[bool, str]:
    import os

    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.profile_lock import clear_stale_profile_lock
    from shorts_bot.browser.stealth import launch_stealth_context

    clear_stale_profile_lock()
    headless = not bool(os.environ.get("DISPLAY"))

    with sync_playwright() as p:
        ctx = launch_stealth_context(p, headless=headless)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(APP_CREATE, wait_until="domcontentloaded", timeout=120000)
        time.sleep(5)

        body = page.inner_text("body") or ""
        if "Select an app type" in body:
            page.get_by_text("Business", exact=True).first.click(force=True, timeout=8000)
            time.sleep(1)
            page.get_by_role("button", name=re.compile("^Next$", re.I)).first.click(force=True, timeout=8000)
            time.sleep(4)

        filled = False
        for sel in (
            page.get_by_label(re.compile(r"App name", re.I)),
            page.locator('input[aria-label*="App name" i]'),
            page.locator('form input[maxlength="30"]'),
        ):
            try:
                if sel.count():
                    sel.first.click(force=True)
                    sel.first.fill(app_name)
                    filled = True
                    break
            except Exception:
                continue
        if not filled:
            inputs = page.locator('input[maxlength="30"]')
            if inputs.count() >= 2:
                inputs.nth(1).fill(app_name)
            elif inputs.count() == 1:
                inputs.first.fill(app_name)

        page.screenshot(path="data/production/_meta_wizard_ready.png", full_page=True)

        body_after = (page.inner_text("body") or "").lower()
        if "re-enter your password" in body_after:
            ctx.close()
            return False, (
                "App form filled. Password popup is on Desktop now — "
                "type password → Submit → then tell agent 'done'"
            )

        # Do NOT auto-click Create app — owner may need to see/confirm
        # Leave browser open 25 min
        console.print("[green]Browser left open on Create app screen.[/green]")
        console.print("[yellow]On Desktop: click the green Create app button.[/yellow]")
        time.sleep(25 * 60)
        ctx.close()

    return True, "Browser session ended — check if app was created"


def open_wizard_browser(*, wait_minutes: int = 25) -> None:
    import os

    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.profile_lock import clear_stale_profile_lock
    from shorts_bot.browser.stealth import launch_stealth_context

    clear_stale_profile_lock()
    console.print(Panel(OWNER_STEPS, title="Create Peripheral Bot app", border_style="green"))
    console.print(f"\n[bold]Opening Desktop Chrome ({wait_minutes} min)…[/bold]\n")

    with sync_playwright() as p:
        ctx = launch_stealth_context(p, headless=not bool(os.environ.get("DISPLAY")))
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(APP_CREATE, wait_until="domcontentloaded", timeout=120000)
        apps = ctx.new_page()
        apps.goto(MY_APPS, wait_until="domcontentloaded", timeout=120000)
        console.print(f"[cyan]Tab 1:[/cyan] {APP_CREATE}")
        console.print(f"[cyan]Tab 2:[/cyan] {MY_APPS}")
        time.sleep(wait_minutes * 60)
        ctx.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Meta app wizard — correct owner steps")
    parser.add_argument("--open-browser", action="store_true", help="Open wizard tabs on Desktop")
    parser.add_argument("--fill", action="store_true", help="Auto-fill Business + app name, leave Create for owner")
    parser.add_argument("--minutes", type=int, default=25)
    args = parser.parse_args()

    if args.fill:
        ok, msg = try_create_app_in_browser()
        console.print(("[green]" if ok else "[yellow]") + msg + "[/]")
        return

    if args.open_browser:
        open_wizard_browser(wait_minutes=args.minutes)
        return

    console.print(Panel(OWNER_STEPS, title="Create Peripheral Bot app", border_style="green"))
    console.print("\nRun: [cyan]python3 -m shorts_bot.integrations.meta_wizard_cli --open-browser[/cyan]")


if __name__ == "__main__":
    main()
