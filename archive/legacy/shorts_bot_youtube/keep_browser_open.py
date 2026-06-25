"""Keep Google sign-in browser open until the user finishes."""

from __future__ import annotations

import time

from rich.console import Console

from shorts_bot.config import settings

console = Console()

SIGNIN_URL = (
    "https://accounts.google.com/signin/v3/identifier"
    "?service=youtube&continue=https://www.youtube.com/create_channel"
)


def main() -> None:
    from playwright.sync_api import sync_playwright

    console.print(
        "[bold green]Opening browser on your Desktop...[/bold green]\n"
        "Sign in to Google (or create account). Phone code if asked.\n"
        "This window stays open for 30 minutes.\n"
        "[yellow]In Cursor: click the Desktop tab to see the browser.[/yellow]"
    )

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(settings.browser_profile_dir),
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(SIGNIN_URL, wait_until="domcontentloaded", timeout=120000)
        console.print(f"[cyan]Loaded:[/cyan] {page.url}")
        console.print("[bold]Waiting 30 minutes for you to sign in...[/bold]")
        time.sleep(1800)
        context.close()


if __name__ == "__main__":
    main()
