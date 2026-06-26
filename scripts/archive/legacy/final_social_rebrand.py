"""Final pass — TikTok display name + Facebook cover/profile."""

from __future__ import annotations

import shutil
import time
import uuid
from pathlib import Path

from playwright.sync_api import sync_playwright

PROFILE = Path("channel/brand/assets/ms_byte/social_profile.png").resolve()
COVER = Path("channel/brand/assets/ms_byte/facebook_cover.png").resolve()
FB_PAGE = "1183615244830685"
TT_NAME = "Rapid Tool Review"


def _copy_chrome() -> Path:
    src = Path("/home/ubuntu/.config/google-chrome")
    dst = Path(f"/tmp/final_{uuid.uuid4().hex[:8]}")
    ignore = lambda _d, n: [x for x in n if x in {"SingletonLock", "SingletonSocket", "SingletonCookie", "DevToolsActivePort"}]
    shutil.copytree(src, dst, ignore=ignore)
    return dst


def facebook(page) -> list[str]:
    logs: list[str] = []
    page.goto(f"https://business.facebook.com/latest/home?asset_id={FB_PAGE}", wait_until="domcontentloaded", timeout=120000)
    time.sleep(5)

    # Cover upload
    page.get_by_text("Add cover photo", exact=False).first.click(force=True)
    time.sleep(1)
    try:
        with page.expect_file_chooser(timeout=12000) as fc:
            page.get_by_text("Upload photo", exact=False).first.click(force=True)
        fc.value.set_files(str(COVER))
        time.sleep(4)
        logs.append("cover selected")
        page.evaluate("""() => {
            const el = [...document.querySelectorAll('span,div,button')]
                .find(e => e.textContent.trim() === 'Save changes');
            el?.click();
        }""")
        time.sleep(5)
        logs.append("cover saved")
    except Exception as exc:
        logs.append(f"cover: {exc}")

    page.screenshot(path="data/browser_screenshots/fb_cover_done.png", full_page=True)

    # Profile — click green P avatar in header
    page.goto(f"https://business.facebook.com/latest/home?asset_id={FB_PAGE}", wait_until="domcontentloaded", timeout=120000)
    time.sleep(4)
    try:
        with page.expect_file_chooser(timeout=12000) as fc:
            page.locator('div[class*="x1rg5ohu"] img, img[src*="scontent"]').first.click(force=True)
        fc.value.set_files(str(PROFILE))
        time.sleep(3)
        logs.append("profile selected")
    except Exception:
        # Click avatar circle near page title
        try:
            with page.expect_file_chooser(timeout=12000) as fc:
                page.evaluate("""() => {
                    const imgs = [...document.querySelectorAll('img')];
                    const av = imgs.find(i => i.width <= 120 && i.height <= 120);
                    av?.click();
                }""")
            fc.value.set_files(str(PROFILE))
            time.sleep(3)
            logs.append("profile selected (js)")
        except Exception as exc:
            logs.append(f"profile: {exc}")

    for label in ("Save", "Save changes", "Apply"):
        btn = page.get_by_text(label, exact=True).first
        if btn.count() and btn.is_visible():
            btn.click()
            logs.append(f"clicked {label}")
            time.sleep(3)
            break

    page.screenshot(path="data/browser_screenshots/fb_profile_done.png", full_page=True)
    return logs


def tiktok(page) -> list[str]:
    logs: list[str] = []
    page.goto("https://www.tiktok.com/@kimberly908931", wait_until="domcontentloaded", timeout=120000)
    time.sleep(4)
    page.locator('button:has-text("Edit profile")').first.click(timeout=15000)
    time.sleep(2)

    # Text inputs only (skip file input for avatar)
    text_inputs = page.locator('input:not([type="file"])')
    count = text_inputs.count()
    logs.append(f"text inputs: {count}")
    if count >= 2:
        name_inp = text_inputs.nth(1)
        name_inp.click()
        name_inp.fill(TT_NAME)
        logs.append("name filled")

    save = page.locator('[data-e2e="edit-profile-save"]')
    if save.is_enabled():
        save.click()
        logs.append("saved")
        time.sleep(4)

    page.goto("https://www.tiktok.com/@kimberly908931", wait_until="domcontentloaded", timeout=120000)
    time.sleep(4)
    page.screenshot(path="data/browser_screenshots/tt_name_done.png", full_page=True)
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
        print("FB:", facebook(page))
        print("TT:", tiktok(page))
        ctx.close()
    shutil.rmtree(chrome, ignore_errors=True)


if __name__ == "__main__":
    main()
