"""Open TurboScribe for voiceover upload + timestamp export (owner handoff)."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from rich.console import Console

console = Console()

TURBOSCRIBE_URL = "https://turboscribe.ai/u"


def open_turboscribe_handoff(*, pack_dir: Path, wait_minutes: int = 20) -> None:
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    vo = pack_dir / "voiceover.mp3"
    if not vo.is_file():
        raise FileNotFoundError(f"No voiceover yet: {vo} — run finish through voiceover step first.")

    console.print(
        "[bold green]Opening TurboScribe on Desktop…[/bold green]\n"
        "[yellow]Click the Desktop tab in Cursor.[/yellow]\n\n"
        f"Voiceover to upload: [cyan]{vo}[/cyan]\n\n"
        "[bold]Steps:[/bold]\n"
        "1. Sign in to TurboScribe\n"
        "2. Upload voiceover.mp3\n"
        "3. Export transcript with timestamps (M:SS lines)\n"
        "4. Save as transcript.txt in the pack folder OR paste into web UI\n\n"
        f"Pack folder: [cyan]{pack_dir}[/cyan]\n"
        f"Window stays open {wait_minutes} minutes.\n"
    )

    with sync_playwright() as p:
        context = launch_stealth_context(p, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(TURBOSCRIBE_URL, wait_until="domcontentloaded", timeout=120000)
        console.print(f"[cyan]Tab:[/cyan] {TURBOSCRIBE_URL}")
        time.sleep(wait_minutes * 60)
        context.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="TurboScribe handoff after voiceover")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--minutes", type=int, default=20)
    args = parser.parse_args()

    from shorts_bot.config import settings

    pack = settings.data_dir / "production" / f"draft_{args.draft_id}"
    open_turboscribe_handoff(pack_dir=pack, wait_minutes=args.minutes)


if __name__ == "__main__":
    main()
