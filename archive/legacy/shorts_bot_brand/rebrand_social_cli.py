"""Rebrand Facebook Page + TikTok profile to Rapid Tool Review / Ms. Byte."""

from __future__ import annotations

import argparse
import shutil
import time
from pathlib import Path
from typing import Callable

from rich.console import Console

console = Console()

FB_PAGE_ID = "1183615244830685"
FB_PROFILE_ID = "61590716288819"

FB_NAME = "Rapid Tool Review"
FB_BIO = (
    "Honest AI tool reviews in ~30 seconds. Ms. Byte — an AI host — breaks down "
    "one real product per Short: strengths, weaknesses, you decide.\n\n"
    "YouTube: @RapidToolReview"
)

TT_NAME = "Rapid Tool Review"
TT_BIO = "Ms. Byte reviews AI tools 📚 Strengths · weaknesses · @RapidToolReview"

SCREENSHOT_DIR = Path("data/browser_screenshots")


def _chrome_copy_dir() -> Path:
    import uuid

    src = Path("/home/ubuntu/.config/google-chrome")
    dst = Path(f"/tmp/social_rebrand_{uuid.uuid4().hex[:8]}")
    if dst.exists():
        shutil.rmtree(dst)

    def ignore(_d: str, names: list[str]) -> list[str]:
        return [n for n in names if n in {"SingletonLock", "SingletonSocket", "SingletonCookie", "DevToolsActivePort"}]

    shutil.copytree(src, dst, ignore=ignore)
    return dst


def _click_text(page, labels: list[str], *, exact: bool = True) -> str | None:
    for label in labels:
        if exact:
            hit = page.evaluate(
                """(label) => {
                const el = [...document.querySelectorAll('span,div,button,a,label')]
                    .find(e => e.textContent.trim() === label);
                if (el) { el.click(); return label; }
                return null;
            }""",
                label,
            )
        else:
            hit = page.evaluate(
                """(label) => {
                const el = [...document.querySelectorAll('span,div,button,a,label')]
                    .find(e => e.textContent.trim().includes(label));
                if (el) { el.click(); return label; }
                return null;
            }""",
                label,
            )
        if hit:
            return str(hit)
    return None


def _dismiss_overlays(page) -> None:
    for _ in range(4):
        _click_text(page, ["Done", "Close", "Not now", "Skip", "Got it", "Dismiss"])
        page.keyboard.press("Escape")
        time.sleep(0.6)


def _save(page, name: str) -> None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SCREENSHOT_DIR / name), full_page=True)


def _upload_file(page, trigger: Callable[[], None], file_path: Path, *, timeout_ms: int = 15_000) -> bool:
    """Click upload trigger; prefer native file chooser, fall back to hidden input."""
    try:
        with page.expect_file_chooser(timeout=timeout_ms) as fc_info:
            trigger()
        fc_info.value.set_files(str(file_path.resolve()))
        time.sleep(3)
        return True
    except Exception:
        pass

    trigger()
    time.sleep(1)
    inputs = page.locator('input[type="file"]')
    if inputs.count():
        inputs.first.set_input_files(str(file_path.resolve()))
        time.sleep(3)
        return True
    return False


def _confirm_save(page) -> None:
    _click_text(
        page,
        ["Save", "Save changes", "Apply", "Confirm", "Done", "Publish", "Update", "Post"],
    )
    time.sleep(2)


def _switch_facebook_page_admin(page) -> bool:
    page.goto(
        f"https://www.facebook.com/profile.php?id={FB_PROFILE_ID}",
        wait_until="domcontentloaded",
        timeout=120_000,
    )
    time.sleep(4)
    _dismiss_overlays(page)
    switched = _click_text(page, ["Switch Now", "Switch"])
    time.sleep(4)
    page.evaluate("""() => document.querySelector('[aria-label="Use Page"]')?.click()""")
    time.sleep(2)
    _dismiss_overlays(page)
    return switched is not None


def _facebook_upload_profile(page, profile: Path, logs: list[str]) -> None:
    page.goto(
        f"https://www.facebook.com/profile.php?id={FB_PROFILE_ID}",
        wait_until="domcontentloaded",
        timeout=120_000,
    )
    time.sleep(3)
    _dismiss_overlays(page)

    page.locator('[aria-label="Profile picture"]').first.click(force=True)
    time.sleep(2)
    if page.locator('input[type="file"]').count():
        page.locator('input[type="file"]').first.set_input_files(str(profile.resolve()))
        time.sleep(4)
        logs.append("uploaded profile")
        _confirm_save(page)


def _facebook_upload_cover(page, cover: Path, logs: list[str]) -> None:
    page.goto(
        f"https://www.facebook.com/profile.php?id={FB_PROFILE_ID}",
        wait_until="domcontentloaded",
        timeout=120_000,
    )
    time.sleep(3)
    _dismiss_overlays(page)

    page.locator('[aria-label="Edit cover photo"]').first.click(force=True)
    time.sleep(2)
    files = page.locator('input[type="file"]')
    if files.count():
        files.last.set_input_files(str(cover.resolve()))
        time.sleep(4)
        logs.append("uploaded cover")
        page.locator('div[role="button"]:has-text("Save changes")').first.click(force=True)
        time.sleep(4)
    else:
        logs.append("cover upload — no file input found")


def _facebook_edit_bio_name(page, logs: list[str]) -> None:
    page.goto(
        f"https://www.facebook.com/profile.php?id={FB_PROFILE_ID}",
        wait_until="domcontentloaded",
        timeout=120_000,
    )
    time.sleep(3)
    _dismiss_overlays(page)

    _click_text(page, ["Edit bio"], exact=False)
    time.sleep(2)

    if page.locator("textarea").count():
        page.locator("textarea").first.fill(FB_BIO)
        logs.append("filled bio")

    for inp in page.locator("input").all()[:12]:
        try:
            val = inp.input_value(timeout=500)
            ph = (inp.get_attribute("placeholder") or "").lower()
            if "Peripheral" in val or "name" in ph or "page name" in ph:
                inp.fill(FB_NAME)
                logs.append("filled page name")
                break
        except Exception:
            pass

    _confirm_save(page)

    # Meta Business Suite fallback for bio/name
    page.goto(
        f"https://business.facebook.com/latest/settings/page_info?asset_id={FB_PAGE_ID}",
        wait_until="domcontentloaded",
        timeout=120_000,
    )
    time.sleep(4)
    _dismiss_overlays(page)
    if page.locator("textarea").count():
        page.locator("textarea").first.fill(FB_BIO)
        logs.append("filled bio (business suite)")
    for inp in page.locator("input").all()[:12]:
        try:
            val = inp.input_value(timeout=500)
            if "Peripheral" in val:
                inp.fill(FB_NAME)
                logs.append("filled page name (business suite)")
                break
        except Exception:
            pass
    _confirm_save(page)


def _tiktok_edit_profile(page, profile: Path, logs: list[str]) -> None:
    page.goto("https://www.tiktok.com/@kimberly908931", wait_until="domcontentloaded", timeout=120_000)
    time.sleep(5)
    page.locator('button:has-text("Edit profile")').first.click(timeout=15000)
    time.sleep(2)
    logs.append("edit profile open")

    file_inputs = page.locator('input[type="file"]')
    if file_inputs.count():
        file_inputs.first.set_input_files(str(profile.resolve()))
        time.sleep(4)
        logs.append("uploaded profile photo")
        try:
            page.locator('button:has-text("Apply")').first.click(timeout=8000)
            time.sleep(3)
        except Exception:
            pass

    if not page.locator('[data-e2e="edit-profile-save"]').count():
        page.locator('button:has-text("Edit profile")').first.click(timeout=10000)
        time.sleep(2)

    text_inputs = page.locator('input:not([type="file"])')
    if text_inputs.count() >= 2:
        try:
            page.get_by_text("Name", exact=True).locator("xpath=following::input[1]").fill(TT_NAME)
            logs.append("filled display name")
        except Exception:
            text_inputs.nth(1).fill(TT_NAME)
            logs.append("filled display name (fallback)")

    if page.locator("textarea").count():
        page.locator("textarea").first.fill(TT_BIO)
        logs.append("filled bio")

    save = page.locator('[data-e2e="edit-profile-save"]')
    if save.is_enabled():
        save.click()
        logs.append("saved")
        time.sleep(2)
        confirm = page.locator('button:has-text("Confirm")').first
        if confirm.count() and confirm.is_visible():
            confirm.click()
            logs.append("confirmed nickname")
        time.sleep(3)

    page.goto("https://www.tiktok.com/@kimberly908931", wait_until="domcontentloaded", timeout=120_000)
    time.sleep(4)
    _save(page, "tiktok_rebrand_done.png")


def rebrand_all(
    *,
    profile: Path,
    fb_cover: Path,
    facebook: bool = True,
    tiktok: bool = True,
) -> dict[str, list[str]]:
    import os

    from playwright.sync_api import sync_playwright

    os.environ["DISPLAY"] = ":1"
    fb_logs: list[str] = []
    tt_logs: list[str] = []
    chrome_dir = _chrome_copy_dir()

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(chrome_dir),
            channel="chrome",
            headless=False,
            viewport={"width": 1500, "height": 1000},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        if facebook:
            console.print("[cyan]Facebook: switching to page admin…[/cyan]")
            if _switch_facebook_page_admin(page):
                fb_logs.append("switched to page admin")
            _save(page, "fb_after_switch.png")

            _facebook_upload_profile(page, profile, fb_logs)
            _save(page, "fb_profile_upload.png")

            _facebook_upload_cover(page, fb_cover, fb_logs)
            _save(page, "fb_cover_upload.png")

            _facebook_edit_bio_name(page, fb_logs)
            _save(page, "fb_rebrand_done.png")

        if tiktok:
            console.print("[cyan]TikTok: edit profile…[/cyan]")
            _tiktok_edit_profile(page, profile, tt_logs)

        ctx.close()

    shutil.rmtree(chrome_dir, ignore_errors=True)
    return {"facebook": fb_logs, "tiktok": tt_logs}


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebrand Facebook + TikTok to Ms. Byte / Rapid Tool Review")
    parser.add_argument("--facebook-only", action="store_true")
    parser.add_argument("--tiktok-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Generate PNGs only, skip browser")
    args = parser.parse_args()

    from shorts_bot.brand.assets import ensure_ms_byte_social_assets

    assets = ensure_ms_byte_social_assets(force=True)
    console.print("[green]Assets ready:[/green]")
    for k, v in assets.items():
        console.print(f"  {k}: {v}")

    if args.dry_run:
        return

    do_fb = not args.tiktok_only
    do_tt = not args.facebook_only

    console.print("[bold]Rebranding Facebook + TikTok in Desktop browser…[/bold]")
    results = rebrand_all(
        profile=assets["profile"],
        fb_cover=assets["facebook_cover"],
        facebook=do_fb,
        tiktok=do_tt,
    )
    for line in results.get("facebook", []):
        console.print(f"  FB: {line}")
    for line in results.get("tiktok", []):
        console.print(f"  TT: {line}")

    console.print("[green]Done.[/green] Check Desktop browser tab + screenshots in data/browser_screenshots/")


if __name__ == "__main__":
    main()
