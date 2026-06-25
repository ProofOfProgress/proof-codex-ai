"""Open InVideo AI Twins setup in Desktop browser."""

from __future__ import annotations

import argparse
import time

from rich.console import Console
from rich.panel import Panel

console = Console()

# InVideo home — AI Twins lives in left nav / Plugins after login
APP_HOME = "https://ai.invideo.io/"


def _open_browser(url: str, *, minutes: int = 20) -> None:
    from shorts_bot.browser.session import _has_display, _launch_context

    if not _has_display():
        console.print(f"[yellow]Open on your PC:[/yellow] {url}")
        return
    pw, context = _launch_context(headless=False)
    try:
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=120000)
        console.print(f"[cyan]Opened:[/cyan] {url}")
        time.sleep(minutes * 60)
    finally:
        context.close()
        pw.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="InVideo AI Twin setup — browser handoff")
    parser.add_argument("--minutes", type=int, default=20)
    args = parser.parse_args()

    console.print(
        Panel(
            "Step 1 — InVideo home (you should already be logged in)\n\n"
            "Step 2 — Left sidebar → **AI Twins** (or Plugins → AI Twins)\n\n"
            "Step 3 — **Express avatar** (fastest) OR upload 30–60 sec video:\n"
            "  • Laptop webcam: look at camera, speak naturally ~30 sec\n"
            "  • OR paste a YouTube link of you talking (if you have one)\n"
            "  • Say the consent line InVideo shows on screen\n\n"
            "Step 4 — **Voice clone** (Plugins → Voices) — optional same session\n"
            "  • Upload 30 sec audio OR use twin bundle\n\n"
            "Step 5 — When twin shows Ready → tell agent **twin done** → v2 generates",
            title="AI Twin setup (do this before v2)",
        )
    )

    _open_browser(APP_HOME, minutes=args.minutes)
    console.print("\n[bold]When twin is Ready:[/bold] say **twin done** in chat")


if __name__ == "__main__":
    main()
