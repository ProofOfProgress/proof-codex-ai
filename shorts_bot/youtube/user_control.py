"""Open browser for the human — no automation, no bot clicks."""

from __future__ import annotations

import time

from rich.console import Console

from shorts_bot.config import settings

console = Console()

# YouTube Studio — you control everything from here
START_URL = "https://studio.youtube.com"


def main() -> None:
    from playwright.sync_api import sync_playwright

    console.print(
        "[bold green]YOU have control.[/bold green]\n"
        "The bot will NOT click anything.\n"
        "Browser stays open for 2 hours.\n"
        "[yellow]Desktop tab in Cursor → use Chrome yourself.[/yellow]"
    )

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(settings.browser_profile_dir),
            headless=False,
            viewport={"width": 1400, "height": 900},
            args=["--start-maximized"],
            no_viewport=False,
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(START_URL, wait_until="domcontentloaded", timeout=120000)
        console.print(f"[cyan]Open:[/cyan] {page.url}")
        console.print("[bold]Bot is hands-off. Close this terminal when you're done.[/bold]")
        time.sleep(7200)
        context.close()


if __name__ == "__main__":
    main()
