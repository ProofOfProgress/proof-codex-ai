"""Upload a finished Short MP4 to Facebook Page as a Reel (browser automation)."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from rich.console import Console

console = Console()


def upload_reel_to_facebook(
    video_path: Path,
    *,
    caption: str,
    page_name: str = "Peripheral",
    wait_seconds: int = 180,
) -> str:
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    if not video_path.is_file():
        raise FileNotFoundError(video_path)

    with sync_playwright() as p:
        context = launch_stealth_context(p, headless=False)
        page = context.pages[0] if context.pages else context.new_page()

        page.goto("https://www.facebook.com/", wait_until="domcontentloaded", timeout=120000)
        time.sleep(4)

        # Open Page if selector exists
        try:
            page.get_by_text(page_name, exact=False).first.click(timeout=8000)
            time.sleep(3)
        except Exception:
            pass

        # Create → Reel
        for label in ("Reel", "Create a reel", "Create reel"):
            try:
                page.get_by_text(label, exact=False).first.click(timeout=8000)
                time.sleep(2)
                break
            except Exception:
                continue

        uploaded = False
        for sel in ('input[type="file"]', 'input[accept*="video"]'):
            loc = page.locator(sel)
            if loc.count():
                loc.first.set_input_files(str(video_path.resolve()), timeout=30000)
                uploaded = True
                break
        if not uploaded:
            try:
                with page.expect_file_chooser(timeout=15000) as fc:
                    page.get_by_text("Upload", exact=False).first.click(timeout=8000)
                fc.value.set_files(str(video_path.resolve()))
                uploaded = True
            except Exception:
                pass
        if not uploaded:
            context.close()
            raise RuntimeError("Could not find Facebook Reel upload control — finish manually in Desktop.")

        time.sleep(10)

        # Caption
        for sel in ('[contenteditable="true"]', 'textarea', '[aria-label*="Describe"]'):
            try:
                loc = page.locator(sel)
                if loc.count() and loc.first.is_visible():
                    loc.first.click(timeout=5000)
                    loc.first.fill(caption[:2200])
                    break
            except Exception:
                continue

        time.sleep(3)

        for label in ("Post", "Share", "Publish", "Next"):
            try:
                btn = page.get_by_role("button", name=label)
                if btn.count() and btn.first.is_visible():
                    btn.first.click(timeout=8000)
                    time.sleep(2)
            except Exception:
                continue

        time.sleep(wait_seconds)
        url = page.url
        context.close()
        return f"Facebook Reel upload attempted — check Desktop. Last URL: {url}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload MP4 to Facebook Reel")
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--caption", default="If a child waves at you on this trail, do not wave back.")
    parser.add_argument("--page", default="Peripheral")
    parser.add_argument("--wait", type=int, default=180)
    args = parser.parse_args()
    msg = upload_reel_to_facebook(
        args.video,
        caption=args.caption,
        page_name=args.page,
        wait_seconds=args.wait,
    )
    console.print(f"[green]{msg}[/green]")


if __name__ == "__main__":
    main()
