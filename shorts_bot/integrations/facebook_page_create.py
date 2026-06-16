"""Create Peripheral Facebook Page via browser (saved profile)."""

from __future__ import annotations

import re
import time

from shorts_bot.integrations.facebook_page_discover import FacebookPageInfo, discover_managed_pages


def create_peripheral_page(*, page_name: str = "Peripheral Horror", category: str = "Entertainment website") -> tuple[list[FacebookPageInfo], str]:
    """
    Create a Facebook Page if none exists. Returns updated page list + status message.
    """
    existing, msg = discover_managed_pages(timeout_sec=20)
    if existing:
        return existing, f"Page already exists — {msg}"

    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.profile_lock import require_unlocked_profile
    from shorts_bot.browser.stealth import launch_stealth_context

    require_unlocked_profile(action="create Facebook Page")

    import os

    headless = not bool(os.environ.get("DISPLAY"))
    with sync_playwright() as p:
        context = launch_stealth_context(p, headless=headless)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.facebook.com/pages/create", wait_until="domcontentloaded", timeout=120000)
        time.sleep(6)

        body = (page.inner_text("body") or "").lower()
        if "sign in" in body or "log in" in body:
            context.close()
            return [], "Facebook not signed in"

        # Page name
        for sel in ('input[placeholder*="Page name" i]', 'input[aria-label*="Page name" i]'):
            loc = page.locator(sel)
            if loc.count():
                try:
                    loc.first.fill(page_name, timeout=5000)
                    break
                except Exception:
                    continue

        time.sleep(1)
        # Category typeahead — must pick a suggestion or Create stays disabled
        cat_filled = False
        for sel in (
            'input[placeholder*="category" i]',
            'input[aria-label*="category" i]',
            'label:has-text("Category") + input',
            'input[type="search"]',
        ):
            loc = page.locator(sel)
            if not loc.count():
                continue
            try:
                box = loc.first
                box.click(timeout=3000)
                box.fill(category, timeout=3000)
                time.sleep(1.5)
                for pick in (category, "Entertainment", "Artist", "Public figure"):
                    try:
                        page.get_by_role("option", name=re.compile(pick, re.I)).first.click(timeout=4000)
                        cat_filled = True
                        break
                    except Exception:
                        try:
                            page.locator(f'[role="option"]:has-text("{pick}")').first.click(timeout=3000)
                            cat_filled = True
                            break
                        except Exception:
                            continue
                if cat_filled:
                    break
            except Exception:
                continue

        if not cat_filled:
            try:
                page.keyboard.press("ArrowDown")
                time.sleep(0.5)
                page.keyboard.press("Enter")
                cat_filled = True
            except Exception:
                pass

        time.sleep(1)
        for label in ("Create Page", "Create", "Next", "Done"):
            try:
                btn = page.get_by_role("button", name=label)
                if btn.count() and btn.first.is_visible():
                    btn.first.click(timeout=5000)
                    break
            except Exception:
                continue

        time.sleep(10)
        try:
            page.screenshot(path="data/production/_facebook_page_create.png", full_page=True)
        except Exception:
            pass
        context.close()

    pages, final_msg = discover_managed_pages(timeout_sec=25)
    if pages:
        return pages, f"Created or found Page — {final_msg}"
    return [], "Page creation attempted — check Desktop browser or data/production/_facebook_page_create.png"
