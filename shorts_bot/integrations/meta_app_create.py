"""Create Meta developer app and wire Graph API Explorer for Page posting."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

from shorts_bot.integrations.facebook_credentials import save_facebook_api_file

APP_CREATE_URL = "https://developers.facebook.com/apps/create/"
EXPLORER = "https://developers.facebook.com/tools/explorer/"
DEFAULT_APP_NAME = "Peripheral Bot"
PAGE_PERMISSIONS = (
    "pages_manage_posts",
    "pages_show_list",
    "pages_read_engagement",
    "pages_manage_metadata",
    "publish_video",
)


def _screenshot(page, name: str) -> None:
    path = Path("data/production") / name
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        page.screenshot(path=str(path), full_page=True)
    except Exception:
        pass


def _body_text(page) -> str:
    try:
        return page.inner_text("body") or ""
    except Exception:
        return ""


def _password_modal_visible(page) -> bool:
    body = _body_text(page).lower()
    return (
        "re-enter your password" in body
        or "please enter your password" in body
        or ("password" in body and "submit" in body and "facebook" in body)
    )


def wait_for_password_clear(page, *, max_wait_sec: int = 600, poll_sec: int = 10) -> bool:
    """Wait for owner to clear Meta password re-entry modal on Desktop."""
    if not _password_modal_visible(page):
        return True
    deadline = time.time() + max_wait_sec
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        remaining = int((deadline - time.time()) / 60)
        print(
            f"[Meta] Waiting for password on Desktop… ({attempt}, ~{remaining} min left)",
            flush=True,
        )
        time.sleep(poll_sec)
        if not _password_modal_visible(page):
            print("[Meta] Password cleared — continuing.", flush=True)
            time.sleep(3)
            return True
    return not _password_modal_visible(page)


def create_meta_app(
    page,
    *,
    app_name: str = DEFAULT_APP_NAME,
    app_type: str = "Business",
) -> str:
    """Create Meta app in browser. Returns app name if created or already exists."""
    page.goto(APP_CREATE_URL, wait_until="domcontentloaded", timeout=120000)
    time.sleep(6)
    _screenshot(page, "_meta_app_create_1.png")

    body = _body_text(page)
    if "Select an app type" in body or "Use cases" in body:
        try:
            page.get_by_text(app_type, exact=True).first.click(force=True, timeout=8000)
            time.sleep(2)
        except Exception:
            page.locator(f'text="{app_type}"').first.click(force=True, timeout=8000)
            time.sleep(2)
        for btn_label in ("Next", "Continue"):
            try:
                page.get_by_role("button", name=re.compile(f"^{btn_label}$", re.I)).first.click(
                    force=True, timeout=6000
                )
                time.sleep(3)
                break
            except Exception:
                continue

    # App name field — must be the form input, NOT the header search box
    filled = False
    for sel in (
        page.get_by_label(re.compile(r"App name", re.I)),
        page.locator('input[aria-label*="App name" i]'),
        page.locator('input[placeholder*="App name" i]'),
        page.locator('form input[maxlength="30"]'),
        page.locator('div:has-text("App name") input[maxlength="30"]'),
    ):
        try:
            if hasattr(sel, "count") and sel.count():
                target = sel.first
                target.click(force=True, timeout=5000)
                target.fill("")
                target.fill(app_name)
                filled = True
                time.sleep(1)
                break
        except Exception:
            continue
    if not filled:
        # Last resort: second maxlength=30 input (first is often header search)
        inputs = page.locator('input[maxlength="30"]')
        if inputs.count() >= 2:
            inputs.nth(1).click(force=True)
            inputs.nth(1).fill(app_name)
        elif inputs.count() == 1:
            inputs.first.click(force=True)
            inputs.first.fill(app_name)
        time.sleep(1)

    for btn_label in ("Create app", "Create App"):
        try:
            page.get_by_role("button", name=re.compile(btn_label, re.I)).first.click(
                force=True, timeout=8000
            )
            time.sleep(4)
            break
        except Exception:
            continue

    _screenshot(page, "_meta_app_create_2.png")
    wait_for_password_clear(page, max_wait_sec=600)
    time.sleep(8)
    _screenshot(page, "_meta_app_create_3.png")

    # Confirm app dashboard or app list shows our app
    page.goto("https://developers.facebook.com/apps/", wait_until="domcontentloaded", timeout=120000)
    time.sleep(6)
    if app_name.lower() in _body_text(page).lower():
        return app_name

    page.goto(EXPLORER, wait_until="domcontentloaded", timeout=120000)
    time.sleep(6)
    if "Create an app to get started" not in _body_text(page):
        return app_name

    raise RuntimeError(
        f"Meta app '{app_name}' may not have been created — check Desktop browser "
        f"(password popup or app review step)."
    )


def select_app_in_explorer(page, *, app_name: str = DEFAULT_APP_NAME) -> None:
    """Pick our Meta app in Graph API Explorer."""
    page.goto(EXPLORER, wait_until="domcontentloaded", timeout=120000)
    time.sleep(8)

    body = _body_text(page)
    if "Create an app to get started" in body:
        raise RuntimeError("No Meta app yet — run create_meta_app first")

    selectors = (
        '[data-testid="SUISearchableSelector/button"]',
        '[aria-label*="Meta App" i]',
        'div[role="button"]:has-text("Graph API Explorer")',
    )
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if loc.count():
                loc.first.click(force=True, timeout=8000)
                time.sleep(2)
                break
        except Exception:
            continue

    try:
        page.get_by_text(app_name, exact=False).first.click(force=True, timeout=8000)
        time.sleep(2)
    except Exception:
        # Fallback: first app in list
        page.locator('[role="menuitem"], [role="option"]').first.click(force=True, timeout=5000)
        time.sleep(2)


def generate_explorer_user_token(page) -> str:
    """Generate user token with Page permissions in Graph API Explorer."""
    for label in ("Get Token", "Generate Access Token"):
        try:
            page.get_by_role("button", name=re.compile(label, re.I)).first.click(force=True, timeout=8000)
            time.sleep(2)
        except Exception:
            pass

    for label in ("Get User Access Token", "Get Page Access Token", "Get Token"):
        try:
            page.get_by_text(label, exact=False).first.click(force=True, timeout=6000)
            time.sleep(3)
            break
        except Exception:
            continue

    for perm in PAGE_PERMISSIONS:
        for sel in (
            page.get_by_label(re.compile(perm, re.I)),
            page.locator(f'label:has-text("{perm}")'),
            page.get_by_text(perm, exact=True),
        ):
            try:
                if hasattr(sel, "count") and sel.count():
                    sel.first.click(force=True, timeout=2000)
                    time.sleep(0.3)
                    break
            except Exception:
                continue

    for label in ("Generate Access Token", "Get Token"):
        try:
            page.get_by_role("button", name=re.compile(label, re.I)).first.click(force=True, timeout=8000)
            time.sleep(5)
            break
        except Exception:
            continue

    for label in ("Continue as", "Continue", "OK", "Done", "Save", "Got it"):
        try:
            btn = page.get_by_role("button", name=re.compile(label, re.I))
            if btn.count():
                btn.first.click(force=True, timeout=5000)
                time.sleep(3)
        except Exception:
            pass

    time.sleep(4)
    _screenshot(page, "_meta_token_explorer.png")

    for sel in (
        'input[placeholder*="Access Token" i]',
        'input[aria-label*="Access Token" i]',
        "textarea",
    ):
        loc = page.locator(sel)
        for i in range(min(loc.count(), 10)):
            try:
                val = (loc.nth(i).input_value() or "").strip()
                if val.startswith("EAA") and len(val) > 40:
                    return val
            except Exception:
                pass
    return ""


def setup_meta_app_and_token(
    *,
    app_name: str = DEFAULT_APP_NAME,
    page_name: str = "Peripheral Horror",
    wait_password_sec: int = 600,
) -> str:
    """Full flow: create app → Explorer token → save Page credentials."""
    import os

    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.profile_lock import require_unlocked_profile
    from shorts_bot.browser.stealth import launch_stealth_context
    from shorts_bot.integrations.meta_token_scrape import resolve_page_token_from_user_token

    require_unlocked_profile(action="create Meta app and Page token")

    headless = not bool(os.environ.get("DISPLAY"))
    with sync_playwright() as p:
        ctx = launch_stealth_context(p, headless=headless)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        create_meta_app(page, app_name=app_name)
        if _password_modal_visible(page):
            if not wait_for_password_clear(page, max_wait_sec=wait_password_sec):
                raise RuntimeError("Password popup still open — type password on Desktop and retry")
        select_app_in_explorer(page, app_name=app_name)
        user_token = generate_explorer_user_token(page)
        ctx.close()

    if not user_token:
        raise RuntimeError(
            "Could not read token from Graph API Explorer. "
            "On Desktop: Get Token → User token → check page permissions → Generate."
        )

    page_id, page_token, name = resolve_page_token_from_user_token(
        user_token, preferred_name=page_name
    )
    path = save_facebook_api_file(
        page_id=page_id,
        page_access_token=page_token,
        page_name=name,
    )
    return f"Meta app '{app_name}' ready — saved Page token → {path} ({name}, id={page_id})"
