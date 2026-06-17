"""Capture what Meta pages actually show on Desktop (debug handoff)."""

from __future__ import annotations

import time
from pathlib import Path

from rich.console import Console

console = Console()

URLS = [
    ("apps", "https://developers.facebook.com/apps/"),
    ("create", "https://developers.facebook.com/apps/create/"),
    ("explorer", "https://developers.facebook.com/tools/explorer/"),
]


def capture_meta_state() -> list[str]:
    import os

    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.profile_lock import clear_stale_profile_lock
    from shorts_bot.browser.stealth import launch_stealth_context

    clear_stale_profile_lock()
    out_dir = Path("data/production")
    out_dir.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    headless = not bool(os.environ.get("DISPLAY"))
    with sync_playwright() as p:
        ctx = launch_stealth_context(p, headless=headless)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        for slug, url in URLS:
            page.goto(url, wait_until="domcontentloaded", timeout=120000)
            time.sleep(6)
            shot = out_dir / f"_meta_capture_{slug}.png"
            page.screenshot(path=str(shot), full_page=True)
            body = (page.inner_text("body") or "").lower()
            lines.append(f"=== {slug} ===")
            lines.append(f"screenshot: {shot}")
            if "peripheral bot" in body:
                lines.append("FOUND: Peripheral Bot app on page")
            if "create an app to get started" in body:
                lines.append("STATE: Explorer — no app yet (Create App modal)")
            if "no apps available" in body:
                lines.append("STATE: No apps in Explorer dropdown")
            if "please re-enter your password" in body:
                lines.append("STATE: Password popup visible")
            if "select an app type" in body:
                lines.append("STATE: App create wizard — pick Business")
            if "app name" in body and "create app" in body:
                lines.append("STATE: App create — Details step (fill name, click Create app)")
            if "my apps" in body and "create app" in body:
                lines.append("STATE: Apps dashboard")
            # Count apps in list
            try:
                cards = page.locator('a[href*="/apps/"]').count()
                lines.append(f"links_with_apps: {cards}")
            except Exception:
                pass
        ctx.close()
    return lines


def main() -> None:
    for line in capture_meta_state():
        console.print(line)


if __name__ == "__main__":
    main()
