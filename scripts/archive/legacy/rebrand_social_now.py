"""One-shot social rebrand — Ms. Byte profile + banner on Facebook & TikTok."""

from __future__ import annotations

import shutil
import time
import uuid
from pathlib import Path

from playwright.sync_api import sync_playwright

PROFILE = Path("channel/brand/assets/ms_byte/social_profile.png").resolve()
COVER = Path("channel/brand/assets/ms_byte/facebook_cover.png").resolve()
SHOT = Path("data/browser_screenshots")
SHOT.mkdir(parents=True, exist_ok=True)

FB_PAGE = "1183615244830685"

FB_BIO = (
    "Honest AI tool reviews in ~30 seconds. Ms. Byte — an AI host — breaks down "
    "one real product per Short: strengths, weaknesses, you decide.\n\n"
    "YouTube: @RapidToolReview"
)
TT_BIO = "Ms. Byte reviews AI tools 📚 Strengths · weaknesses · @RapidToolReview"
TT_NAME = "Rapid Tool Review"


def _copy_chrome() -> Path:
    src = Path("/home/ubuntu/.config/google-chrome")
    dst = Path(f"/tmp/rebrand_{uuid.uuid4().hex[:8]}")
    ignore = lambda _d, names: [n for n in names if n in {"SingletonLock", "SingletonSocket", "SingletonCookie", "DevToolsActivePort"}]
    shutil.copytree(src, dst, ignore=ignore)
    return dst


def _snap(page, name: str) -> None:
    page.screenshot(path=str(SHOT / name), full_page=True)


def _dismiss_fb(page) -> None:
    page.evaluate(
        """() => {
        document.querySelector('[aria-label="Use Page"]')?.click();
        for (const t of ['Done','Close','Not now']) {
            [...document.querySelectorAll('div[role="button"],span')]
                .find(e => e.textContent.trim() === t)?.click();
        }
    }"""
    )
    page.keyboard.press("Escape")
    time.sleep(1.5)


def _upload_via_chooser(page, click_js: str, file_path: Path) -> bool:
    try:
        with page.expect_file_chooser(timeout=12_000) as fc:
            page.evaluate(click_js)
        fc.value.set_files(str(file_path))
        time.sleep(3)
        return True
    except Exception:
        return False


def facebook(page) -> list[str]:
    logs: list[str] = []

    # Meta Business Suite — profile + cover
    page.goto(f"https://business.facebook.com/latest/home?asset_id={FB_PAGE}", wait_until="domcontentloaded", timeout=120000)
    time.sleep(5)
    _dismiss_fb(page)
    _snap(page, "fb_mbs_home.png")

    # Cover via "Add cover photo" button in MBS header
    add_cover = page.get_by_text("Add cover photo", exact=False).first
    if add_cover.count():
        try:
            with page.expect_file_chooser(timeout=12_000) as fc:
                add_cover.click(force=True)
                time.sleep(1)
                upload = page.get_by_text("Upload photo", exact=False).first
                if upload.count():
                    upload.click(force=True)
            fc.value.set_files(str(COVER))
            time.sleep(4)
            logs.append("cover uploaded")
            page.get_by_text("Save", exact=True).first.click(timeout=5000)
            time.sleep(3)
        except Exception as exc:
            logs.append(f"cover err: {exc}")
    _snap(page, "fb_after_cover.png")

    # Profile via avatar area in MBS header
    page.goto(f"https://business.facebook.com/latest/home?asset_id={FB_PAGE}", wait_until="domcontentloaded", timeout=120000)
    time.sleep(4)
    _dismiss_fb(page)

    # Profile — click avatar in MBS page header
    try:
        with page.expect_file_chooser(timeout=12_000) as fc:
            page.locator('img[alt*="Peripheral"], img[alt*="profile"]').first.click(force=True)
            time.sleep(1)
            upd = page.get_by_text("Update profile picture", exact=False).first
            if upd.count():
                upd.click(force=True)
            else:
                page.get_by_text("Upload photo", exact=False).first.click(force=True)
        fc.value.set_files(str(PROFILE))
        time.sleep(4)
        logs.append("profile uploaded")
        page.get_by_text("Save", exact=True).first.click(timeout=5000)
        time.sleep(3)
    except Exception as exc:
        logs.append(f"profile err: {exc}")
    _snap(page, "fb_after_profile.png")

    # Page name + bio
    page.goto(f"https://business.facebook.com/latest/settings/page_info?asset_id={FB_PAGE}", wait_until="domcontentloaded", timeout=120000)
    time.sleep(5)
    _dismiss_fb(page)

    for inp in page.locator("input").all()[:20]:
        try:
            v = inp.input_value(timeout=400)
            if "Peripheral" in v or v.strip() == "Peripheral Horror":
                inp.fill("Rapid Tool Review")
                logs.append("page name filled")
        except Exception:
            pass

    for ta in page.locator("textarea").all()[:5]:
        try:
            ta.fill(FB_BIO)
            logs.append("bio filled")
            break
        except Exception:
            pass

    page.evaluate(
        """() => {
        for (const t of ['Save','Save changes']) {
            const el = [...document.querySelectorAll('div[role="button"],span,button')]
                .find(e => e.textContent.trim() === t);
            if (el) { el.click(); return; }
        }
    }"""
    )
    time.sleep(3)
    _snap(page, "fb_final.png")
    return logs


def tiktok(page) -> list[str]:
    logs: list[str] = []
    page.goto("https://www.tiktok.com/@kimberly908931", wait_until="domcontentloaded", timeout=120000)
    time.sleep(5)

    page.locator('button:has-text("Edit profile")').first.click(timeout=15000)
    time.sleep(2)
    logs.append("edit profile open")

    # Avatar — click pencil overlay on profile photo
    avatar = page.locator('[data-e2e="edit-profile-avatar"], div[class*="DivProfilePhoto"]').first
    try:
        with page.expect_file_chooser(timeout=12_000) as fc:
            avatar.click(force=True)
        fc.value.set_files(str(PROFILE))
        time.sleep(4)
        logs.append("avatar uploaded")
        try:
            page.locator('button:has-text("Apply")').first.click(timeout=8000)
            time.sleep(3)
            logs.append("avatar cropped")
        except Exception:
            pass
    except Exception as exc:
        logs.append(f"avatar err: {exc}")

    # Re-open if modal closed
    if not page.locator('[data-e2e="edit-profile-save"]').count():
        page.locator('button:has-text("Edit profile")').first.click(timeout=10000)
        time.sleep(2)

    # Name = second text input (first is username)
    text_inputs = page.locator('input[type="text"]')
    if text_inputs.count() >= 2:
        text_inputs.nth(1).fill(TT_NAME)
        logs.append("display name filled")

    ta = page.locator("textarea").first
    if ta.count():
        ta.fill(TT_BIO)
        logs.append(f"bio filled ({len(TT_BIO)} chars)")

    _snap(page, "tt_before_save.png")

    save = page.locator('[data-e2e="edit-profile-save"]:not([disabled])')
    try:
        page.locator('[data-e2e="edit-profile-save"]').click(timeout=15000, force=True)
        logs.append("saved profile")
        time.sleep(4)
    except Exception as exc:
        logs.append(f"save err: {exc}")

    page.goto("https://www.tiktok.com/@kimberly908931", wait_until="domcontentloaded", timeout=120000)
    time.sleep(4)
    _snap(page, "tt_final.png")
    return logs


def main() -> None:
    import os

    os.environ["DISPLAY"] = ":1"
    chrome = _copy_chrome()
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(chrome),
            channel="chrome",
            headless=False,
            viewport={"width": 1500, "height": 1000},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        print("=== Facebook ===")
        for line in facebook(page):
            print(" ", line)
        print("=== TikTok ===")
        for line in tiktok(page):
            print(" ", line)
        ctx.close()
    shutil.rmtree(chrome, ignore_errors=True)


if __name__ == "__main__":
    main()
