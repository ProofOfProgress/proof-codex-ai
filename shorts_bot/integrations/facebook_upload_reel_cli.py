"""Upload a finished Short MP4 to Facebook Page as a Reel (browser automation)."""

from __future__ import annotations

import argparse
import re
import time
from pathlib import Path

from rich.console import Console

console = Console()


def upload_reel_to_facebook(
    video_path: Path,
    *,
    caption: str,
    page_name: str = "Peripheral Horror",
    page_id: str = "61590716288819",
    wait_seconds: int = 180,
) -> str:
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    if not video_path.is_file():
        raise FileNotFoundError(video_path)

    with sync_playwright() as p:
        context = launch_stealth_context(p, headless=False)
        page = context.pages[0] if context.pages else context.new_page()

        page.goto(
            f"https://www.facebook.com/profile.php?id={page_id}",
            wait_until="domcontentloaded",
            timeout=120000,
        )
        time.sleep(5)

        for label in ("Switch", "Switch Now"):
            try:
                page.get_by_role("button", name=__import__("re").compile(label, __import__("re").I)).first.click(timeout=8000)
                time.sleep(4)
                break
            except Exception:
                pass

        for url in (
            f"https://www.facebook.com/reels/create/?page_id={page_id}",
            "https://business.facebook.com/latest/reels_composer",
            f"https://www.facebook.com/profile.php?id={page_id}",
        ):
            page.goto(url, wait_until="domcontentloaded", timeout=120000)
            time.sleep(5)
            if page.locator('input[type="file"]').count():
                break

        # Create → Reel from Page home
        for label in ("Reel", "Create a reel", "Create reel", "Create"):
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

        time.sleep(8)

        # Step 1: Create reel → Next
        for label in ("Next",):
            try:
                page.get_by_role("button", name=re.compile(label, re.I)).first.click(timeout=10000)
                time.sleep(6)
                break
            except Exception:
                pass

        # Step 2: Edit reel → caption
        caption_filled = False
        try:
            box = page.get_by_placeholder(re.compile(r"Describe your reel", re.I))
            if box.count():
                box.first.click(timeout=5000)
                box.first.fill(caption[:2200])
                caption_filled = True
        except Exception:
            pass
        if not caption_filled:
            for sel in (
                'textarea[placeholder*="Describe" i]',
                '[contenteditable="true"]',
                "textarea",
            ):
                try:
                    loc = page.locator(sel)
                    if loc.count() and loc.first.is_visible():
                        loc.first.click(timeout=5000)
                        loc.first.fill(caption[:2200])
                        caption_filled = True
                        break
                except Exception:
                    continue

        time.sleep(2)

        # Step 3: Edit reel → Next (to settings)
        try:
            page.get_by_role("button", name=re.compile(r"^Next$", re.I)).first.click(timeout=10000)
            time.sleep(6)
        except Exception:
            pass

        # Step 4: Reel settings → Post (change audience to Public if Page)
        time.sleep(3)
        try:
            page.get_by_text(re.compile(r"Friends", re.I)).first.click(timeout=5000)
            time.sleep(2)
            for pub in ("Public", "Everyone"):
                try:
                    page.get_by_text(pub, exact=True).first.click(timeout=5000)
                    time.sleep(1)
                    break
                except Exception:
                    pass
        except Exception:
            pass

        for label in ("Post", "Share", "Publish", "Share now", "Done"):
            try:
                btn = page.get_by_role("button", name=re.compile(label, re.I))
                for i in range(min(btn.count(), 3)):
                    if btn.nth(i).is_visible():
                        btn.nth(i).click(timeout=10000)
                        time.sleep(8)
                        break
            except Exception:
                continue

        time.sleep(wait_seconds)
        page.screenshot(path="data/production/_facebook_reel_upload.png", full_page=True)
        url = page.url
        context.close()
        return f"Facebook Reel upload attempted — screenshot data/production/_facebook_reel_upload.png — URL: {url}"


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
