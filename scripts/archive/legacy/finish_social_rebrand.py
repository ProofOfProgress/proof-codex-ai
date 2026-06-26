"""Finish social rebrand — save FB cover, upload profile pics, complete TikTok."""

from __future__ import annotations

import shutil
import time
import uuid
from pathlib import Path

from playwright.sync_api import sync_playwright

PROFILE = Path("channel/brand/assets/ms_byte/social_profile.png").resolve()
COVER = Path("channel/brand/assets/ms_byte/facebook_cover.png").resolve()
FB_PAGE = "1183615244830685"
TT_BIO = "Ms. Byte reviews AI tools 📚 Strengths · weaknesses · @RapidToolReview"
TT_NAME = "Rapid Tool Review"


def _copy_chrome() -> Path:
    src = Path("/home/ubuntu/.config/google-chrome")
    dst = Path(f"/tmp/finish_{uuid.uuid4().hex[:8]}")
    ignore = lambda _d, n: [x for x in n if x in {"SingletonLock", "SingletonSocket", "SingletonCookie", "DevToolsActivePort"}]
    shutil.copytree(src, dst, ignore=ignore)
    return dst


def finish_facebook(page) -> list[str]:
    logs: list[str] = []
    page.goto(f"https://business.facebook.com/latest/home?asset_id={FB_PAGE}", wait_until="domcontentloaded", timeout=120000)
    time.sleep(5)

    # Save cover if reposition UI is open
    save_changes = page.get_by_text("Save changes", exact=True).first
    if save_changes.count() and save_changes.is_visible():
        save_changes.click()
        logs.append("saved cover")
        time.sleep(4)

    page.screenshot(path="data/browser_screenshots/fb_finish1.png", full_page=True)

    # Profile via Settings → Profiles
    page.goto(f"https://business.facebook.com/latest/settings/profiles?asset_id={FB_PAGE}", wait_until="domcontentloaded", timeout=120000)
    time.sleep(5)

    try:
        with page.expect_file_chooser(timeout=15000) as fc:
            page.get_by_text("Update", exact=False).first.click(force=True)
        fc.value.set_files(str(PROFILE))
        time.sleep(4)
        logs.append("profile file set")
        page.get_by_text("Save", exact=True).first.click(timeout=8000)
        time.sleep(3)
        logs.append("profile saved")
    except Exception as exc:
        logs.append(f"profile via settings: {exc}")
        # Fallback: click profile image on home
        page.goto(f"https://business.facebook.com/latest/home?asset_id={FB_PAGE}", wait_until="domcontentloaded", timeout=120000)
        time.sleep(4)
        try:
            with page.expect_file_chooser(timeout=15000) as fc:
                page.locator("img").first.click(force=True)
            fc.value.set_files(str(PROFILE))
            time.sleep(3)
            page.get_by_text("Save", exact=True).first.click(timeout=8000)
            logs.append("profile saved (fallback)")
        except Exception as exc2:
            logs.append(f"profile fallback: {exc2}")

    page.screenshot(path="data/browser_screenshots/fb_finish2.png", full_page=True)
    return logs


def finish_tiktok(page) -> list[str]:
    logs: list[str] = []
    page.goto("https://www.tiktok.com/@kimberly908931", wait_until="domcontentloaded", timeout=120000)
    time.sleep(4)
    page.locator('button:has-text("Edit profile")').first.click(timeout=15000)
    time.sleep(2)

    # Name
    inputs = page.locator('input[type="text"]')
    n = inputs.count()
    logs.append(f"found {n} text inputs")
    if n >= 2:
        inputs.nth(1).click()
        inputs.nth(1).fill("")
        inputs.nth(1).type(TT_NAME, delay=30)
        logs.append("name typed")

    page.locator("textarea").first.fill(TT_BIO)
    logs.append("bio filled")

    # Photo via hidden input if present
    file_inputs = page.locator('input[type="file"]')
    if file_inputs.count():
        file_inputs.first.set_input_files(str(PROFILE))
        time.sleep(4)
        logs.append("photo via input")
        try:
            page.locator('button:has-text("Apply")').first.click(timeout=8000)
            time.sleep(3)
        except Exception:
            pass

    page.screenshot(path="data/browser_screenshots/tt_finish_before_save.png", full_page=True)

    save = page.locator('[data-e2e="edit-profile-save"]')
    enabled = save.is_enabled(timeout=3000) if save.count() else False
    logs.append(f"save enabled: {enabled}")
    if enabled:
        save.click()
        logs.append("saved")
        time.sleep(4)

    page.goto("https://www.tiktok.com/@kimberly908931", wait_until="domcontentloaded", timeout=120000)
    time.sleep(4)
    page.screenshot(path="data/browser_screenshots/tt_finish_final.png", full_page=True)
    return logs


def main() -> None:
    import os

    os.environ["DISPLAY"] = ":1"
    chrome = _copy_chrome()
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(chrome), channel="chrome", headless=False,
            viewport={"width": 1500, "height": 1000},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        print("FB:", finish_facebook(page))
        print("TT:", finish_tiktok(page))
        ctx.close()
    shutil.rmtree(chrome, ignore_errors=True)


if __name__ == "__main__":
    main()
