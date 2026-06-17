"""Polish Peripheral Horror Facebook Page — bio, photos, algorithm-friendly fields."""

from __future__ import annotations

import re
import time
from pathlib import Path

PAGE_ID = "61590716288819"
PAGE_NAME = "Peripheral Horror"
BIO = "Scary micro-stories from the woods. New horror Short every day. don't blink."
ABOUT = (
    "Peripheral Horror — hand-drawn scary micro-stories (~30 seconds). "
    "Pine forests, the Lost Boy, things that shouldn't wave back. "
    "Watch to the end. Use headphones."
)
WEBSITE = "https://youtube.com/@PeripheralHorror"
HASHTAGS = "#horror #scarystories #creepy #lostinthewoods #folklore"


def _best_profile_image(pack_dir: Path | None = None) -> Path | None:
    candidates = []
    if pack_dir and pack_dir.is_dir():
        images = pack_dir / "images"
        for name in ("00.11.png", "00.13.png", "00.07.png", "00.22.png"):
            p = images / name
            if p.is_file():
                candidates.append(p)
    brand = Path("channel/brand/logo.png")
    if brand.is_file():
        candidates.append(brand)
    return candidates[0] if candidates else None


def polish_facebook_page(*, pack_dir: Path | None = None, wait_sec: int = 8) -> list[str]:
    """Browser polish: profile photo, about text, professional dashboard fields."""
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.profile_lock import require_unlocked_profile
    from shorts_bot.browser.stealth import launch_stealth_context

    require_unlocked_profile(action="polish Facebook Page")
    import os

    headless = not bool(os.environ.get("DISPLAY"))
    lines: list[str] = []
    profile_img = _best_profile_image(pack_dir)

    with sync_playwright() as p:
        context = launch_stealth_context(p, headless=headless)
        page = context.pages[0] if context.pages else context.new_page()

        # Page settings / About
        page.goto(
            f"https://www.facebook.com/profile.php?id={PAGE_ID}&sk=about",
            wait_until="domcontentloaded",
            timeout=120000,
        )
        time.sleep(wait_sec)

        # Switch into Page profile (required for edit controls)
        for label in ("Switch", "Switch Now", "Switch into"):
            try:
                page.get_by_role("button", name=re.compile(label, re.I)).first.click(timeout=8000)
                time.sleep(4)
                lines.append("Switched into Page profile")
                break
            except Exception:
                pass

        body = (page.inner_text("body") or "").lower()
        if "sign in" in body[:400]:
            context.close()
            return ["Facebook not signed in"]

        # Try edit bio / description
        for label in ("Edit bio", "Add bio", "Edit Page info", "Edit details"):
            try:
                page.get_by_role("button", name=re.compile(label, re.I)).first.click(timeout=5000)
                time.sleep(2)
                break
            except Exception:
                continue

        for sel in ('textarea[aria-label*="bio" i]', 'textarea', 'div[contenteditable="true"]'):
            loc = page.locator(sel)
            if loc.count():
                try:
                    loc.first.fill(BIO, timeout=5000)
                    lines.append("Bio field filled")
                    break
                except Exception:
                    continue

        for label in ("Save", "Done", "Publish"):
            try:
                page.get_by_role("button", name=re.compile(label, re.I)).first.click(timeout=4000)
                time.sleep(2)
                break
            except Exception:
                pass

        # Profile + cover photo upload
        page.goto(
            f"https://www.facebook.com/profile.php?id={PAGE_ID}",
            wait_until="domcontentloaded",
            timeout=120000,
        )
        time.sleep(wait_sec)

        if profile_img and profile_img.is_file():
            for label in ("Edit profile photo", "Add profile picture", "Update profile picture"):
                try:
                    with page.expect_file_chooser(timeout=15000) as fc:
                        page.get_by_role("button", name=re.compile(label, re.I)).first.click(timeout=8000)
                    fc.value.set_files(str(profile_img.resolve()))
                    time.sleep(4)
                    for save in ("Save", "Done", "Set as profile picture"):
                        try:
                            page.get_by_role("button", name=re.compile(save, re.I)).first.click(timeout=5000)
                            break
                        except Exception:
                            pass
                    lines.append(f"Profile photo uploaded from {profile_img.name}")
                    break
                except Exception:
                    try:
                        cam = page.locator('[aria-label*="profile photo" i]')
                        if cam.count():
                            with page.expect_file_chooser(timeout=12000) as fc:
                                cam.first.click(timeout=5000)
                            fc.value.set_files(str(profile_img.resolve()))
                            lines.append(f"Profile photo set via camera icon ({profile_img.name})")
                            break
                    except Exception:
                        continue

            # Cover — use same or wide still
            cover = profile_img
            for label in ("Edit cover photo", "Add cover photo", "Upload cover photo"):
                try:
                    with page.expect_file_chooser(timeout=15000) as fc:
                        page.get_by_role("button", name=re.compile(label, re.I)).first.click(timeout=8000)
                    fc.value.set_files(str(cover.resolve()))
                    time.sleep(4)
                    for save in ("Save", "Done", "Confirm"):
                        try:
                            page.get_by_role("button", name=re.compile(save, re.I)).first.click(timeout=5000)
                            break
                        except Exception:
                            pass
                    lines.append("Cover photo uploaded")
                    break
                except Exception:
                    continue

        # Professional dashboard — add website if available
        page.goto(
            f"https://www.facebook.com/profile.php?id={PAGE_ID}&sk=about_contact_and_basic_info",
            wait_until="domcontentloaded",
            timeout=120000,
        )
        time.sleep(5)
        try:
            page.get_by_text("Website", exact=False).first.click(timeout=5000)
            time.sleep(1)
            inp = page.locator('input[type="url"], input[placeholder*="http"]')
            if inp.count():
                inp.first.fill(WEBSITE)
                page.get_by_role("button", name=re.compile("Save", re.I)).first.click(timeout=5000)
                lines.append(f"Website set: {WEBSITE}")
        except Exception:
            pass

        shot = Path("data/production/_facebook_polish.png")
        page.screenshot(path=str(shot), full_page=True)
        lines.append(f"Screenshot: {shot}")
        context.close()

    if not lines:
        lines.append("Page polish attempted — check Desktop browser")
    return lines
