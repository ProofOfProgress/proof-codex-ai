"""Open Meta app setup on Desktop — owner does password + Create app by hand."""

from __future__ import annotations

import argparse
import time

from rich.console import Console
from rich.panel import Panel

console = Console()

APP_CREATE = "https://developers.facebook.com/apps/create/"
MY_APPS = "https://developers.facebook.com/apps/"
EXPLORER = "https://developers.facebook.com/tools/explorer/"

OWNER_STEPS = """
[bold]You were right — no password on these screens yet.[/bold]

The app [bold]Peripheral Bot[/bold] is filled in on Desktop. One click left:

1. Click the [bold cyan]Desktop[/bold cyan] tab in Cursor
2. Open the Chrome tab [bold]"Create an app"[/bold]
3. You should see App name = [bold cyan]Peripheral Bot[/bold cyan]
4. Click the green [bold]Create app[/bold] button (bottom right)

[dim]Facebook may ask for your password ONLY after that click.
If a popup appears then, type password → Submit.
If nothing asks for password, the app was created — tell agent "done".[/dim]
"""


def open_meta_owner_handoff(*, wait_minutes: int = 30) -> None:
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.profile_lock import clear_stale_profile_lock
    from shorts_bot.browser.stealth import launch_stealth_context

    clear_stale_profile_lock()

    console.print(Panel(OWNER_STEPS, title="Meta app — your 2-minute step", border_style="yellow"))
    console.print(
        f"\n[bold green]Opening Chrome on your Desktop now…[/bold green]\n"
        f"[yellow]Click the Desktop tab in Cursor.[/yellow]\n"
        f"Window stays open {wait_minutes} minutes.\n"
    )

    tabs = [
        (APP_CREATE, "Create app (Peripheral Bot)"),
        (MY_APPS, "My apps (check if it exists)"),
        (EXPLORER, "Graph API Explorer (token later)"),
    ]

    with sync_playwright() as p:
        context = launch_stealth_context(p, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        for i, (url, label) in enumerate(tabs):
            if i == 0:
                page.goto(url, wait_until="domcontentloaded", timeout=120000)
            else:
                new_page = context.new_page()
                new_page.goto(url, wait_until="domcontentloaded", timeout=120000)
            console.print(f"[cyan]Tab {i + 1} — {label}:[/cyan] {url}")
        console.print(
            "\n[bold]When done (app created), tell the agent:[/bold] "
            "[cyan]password done[/cyan] or [cyan]app created[/cyan]\n"
        )
        time.sleep(wait_minutes * 60)
        context.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Open Meta app setup on Desktop for owner")
    parser.add_argument("--minutes", type=int, default=30)
    args = parser.parse_args()
    open_meta_owner_handoff(wait_minutes=args.minutes)


if __name__ == "__main__":
    main()
