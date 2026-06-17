"""Scrape Meta Graph API Explorer token and resolve Page access token."""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from shorts_bot.integrations.facebook_credentials import save_facebook_api_file

GRAPH = "https://graph.facebook.com/v21.0"
EXPLORER = "https://developers.facebook.com/tools/explorer/"


def _graph_get(path: str, token: str) -> dict:
    url = f"{GRAPH}/{path.lstrip('/')}?access_token={urllib.parse.quote(token)}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read().decode())


def resolve_page_token_from_user_token(user_token: str, *, preferred_name: str = "Peripheral") -> tuple[str, str, str]:
    """Return (page_id, page_access_token, page_name) from a user access token."""
    data = _graph_get("me/accounts?fields=name,id,access_token", user_token)
    accounts = data.get("data") or []
    if not accounts:
        raise RuntimeError("Token has no Pages — create Peripheral Page first")
    preferred = preferred_name.lower()
    for acct in accounts:
        if preferred in str(acct.get("name") or "").lower():
            return (
                str(acct["id"]),
                str(acct["access_token"]),
                str(acct.get("name") or preferred_name),
            )
    first = accounts[0]
    return str(first["id"]), str(first["access_token"]), str(first.get("name") or "")


REGISTER = "https://developers.facebook.com/async/registration/"


def _register_as_developer(page) -> None:
    """Complete one-time Meta developer registration if prompted."""
    page.goto(REGISTER, wait_until="domcontentloaded", timeout=120000)
    time.sleep(6)
    for label in (
        "Get started",
        "Continue",
        "Next",
        "Confirm",
        "I agree",
        "Agree",
        "Submit",
        "Save",
    ):
        try:
            btn = page.get_by_role("button", name=re.compile(label, re.I))
            if btn.count():
                btn.first.click(force=True, timeout=5000)
                time.sleep(3)
        except Exception:
            pass
        try:
            link = page.get_by_role("link", name=re.compile(label, re.I))
            if link.count():
                link.first.click(force=True, timeout=5000)
                time.sleep(3)
        except Exception:
            pass
    # Accept checkboxes if present
    for sel in ('input[type="checkbox"]', '[role="checkbox"]'):
        try:
            boxes = page.locator(sel)
            for i in range(min(boxes.count(), 4)):
                boxes.nth(i).click(force=True, timeout=2000)
                time.sleep(0.5)
        except Exception:
            pass


def scrape_explorer_user_token(*, wait_sec: int = 15) -> str:
    """Read user access token from Graph API Explorer (owner must be logged in)."""
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.profile_lock import require_unlocked_profile
    from shorts_bot.browser.stealth import launch_stealth_context

    require_unlocked_profile(action="read Meta Graph API Explorer token")

    import os

    headless = not bool(os.environ.get("DISPLAY"))
    with sync_playwright() as p:
        context = launch_stealth_context(p, headless=headless)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(EXPLORER, wait_until="domcontentloaded", timeout=120000)
        time.sleep(8)
        if "explorer" not in page.url.lower():
            page.goto(EXPLORER, wait_until="networkidle", timeout=120000)
            time.sleep(6)

        body = (page.inner_text("body") or "").lower()
        if "register as a facebook developer" in body or "aren't registered" in body:
            clicked = False
            for sel in (
                page.get_by_role("link", name=re.compile("Register", re.I)),
                page.get_by_role("button", name=re.compile("Register", re.I)),
                page.locator('a:has-text("Register")'),
            ):
                try:
                    if hasattr(sel, "count") and sel.count():
                        sel.first.click(force=True, timeout=8000)
                        clicked = True
                        break
                except Exception:
                    continue
            if clicked:
                time.sleep(10)
                _register_as_developer(page)
            page.goto(EXPLORER, wait_until="domcontentloaded", timeout=120000)
            time.sleep(8)

        # Select Peripheral Bot app if dropdown visible
        try:
            page.locator('text=Peripheral Bot').first.click(force=True, timeout=3000)
        except Exception:
            pass

        # Add permissions via "Add a Permission" combobox
        perms = (
            "pages_manage_posts",
            "pages_show_list",
            "pages_read_engagement",
            "pages_manage_metadata",
            "publish_video",
        )
        for perm in perms:
            try:
                add = page.get_by_text("Add a Permission", exact=False)
                if add.count():
                    add.first.click(force=True, timeout=3000)
                    time.sleep(0.5)
                page.get_by_text(perm, exact=True).first.click(force=True, timeout=3000)
                time.sleep(0.4)
            except Exception:
                try:
                    page.locator(f'[role="option"]:has-text("{perm}")').first.click(
                        force=True, timeout=2000
                    )
                    time.sleep(0.4)
                except Exception:
                    pass

        # Generate token — opens OAuth (owner may need to click Continue on Desktop)
        for label in ("Generate Access Token",):
            try:
                page.get_by_role("button", name=re.compile(label, re.I)).first.click(
                    force=True, timeout=8000
                )
                time.sleep(4)
            except Exception:
                pass

        for label in ("Get User Access Token", "Get Page Access Token"):
            try:
                page.get_by_text(label, exact=False).first.click(force=True, timeout=5000)
                time.sleep(3)
            except Exception:
                pass

        # OAuth confirm — poll up to 3 min for owner to click Continue on Desktop
        deadline = time.time() + 180
        token = ""
        while time.time() < deadline:
            for label in ("Continue as", "Continue", "OK", "Done", "Save", "Got it"):
                try:
                    btn = page.get_by_role("button", name=re.compile(label, re.I))
                    if btn.count():
                        btn.first.click(force=True, timeout=3000)
                        time.sleep(2)
                except Exception:
                    pass
            for sel in (
                'input[placeholder*="Access Token" i]',
                'input[aria-label*="Access Token" i]',
                "textarea",
            ):
                loc = page.locator(sel)
                for i in range(min(loc.count(), 8)):
                    try:
                        val = (loc.nth(i).input_value() or "").strip()
                        if val.startswith("EAA") and len(val) > 40:
                            token = val
                            break
                    except Exception:
                        pass
                if token:
                    break
            if token:
                break
            time.sleep(5)

        if not token:
            # Legacy permission checkboxes
            for perm in ("pages_manage_posts", "pages_show_list", "pages_read_engagement"):
                try:
                    cb = page.get_by_label(re.compile(perm, re.I))
                    if cb.count():
                        cb.first.check(force=True, timeout=3000)
                except Exception:
                    pass

            for label in (
                "Generate Access Token",
                "Get Page Access Token",
                "Get User Access Token",
                "Get Token",
            ):
                try:
                    btn = page.get_by_role("button", name=re.compile(label, re.I))
                    if btn.count():
                        btn.first.click(force=True, timeout=8000)
                        time.sleep(5)
                        break
                except Exception:
                    continue

            for label in ("Continue as", "Continue", "OK", "Done", "Save"):
                try:
                    btn = page.get_by_role("button", name=re.compile(label, re.I))
                    if btn.count():
                        btn.first.click(force=True, timeout=5000)
                        time.sleep(3)
                except Exception:
                    pass

            for sel in (
                'input[placeholder*="Access Token" i]',
                'input[aria-label*="Access Token" i]',
                "textarea",
            ):
                loc = page.locator(sel)
                for i in range(min(loc.count(), 8)):
                    try:
                        val = (loc.nth(i).input_value() or "").strip()
                        if val.startswith("EAA") and len(val) > 40:
                            token = val
                            break
                    except Exception:
                        pass
                if token:
                    break

        page.screenshot(path="data/production/_meta_token_scrape.png", full_page=True)
        context.close()

    if not token:
        raise RuntimeError(
            "Could not read access token from Graph API Explorer. "
            "On Desktop: Graph API Explorer → Generate Access Token → Continue as you → retry."
        )
    return token


def setup_meta_page_api(*, page_name: str = "Peripheral Horror") -> str:
    """Full Meta API setup: scrape user token → resolve page token → save."""
    user_token = scrape_explorer_user_token()
    page_id, page_token, name = resolve_page_token_from_user_token(user_token, preferred_name=page_name)
    path = save_facebook_api_file(
        page_id=page_id,
        page_access_token=page_token,
        page_name=name,
    )
    return f"Saved Facebook API credentials → {path} (Page: {name}, id={page_id})"


def probe_saved_credentials() -> tuple[bool, str]:
    from shorts_bot.integrations.facebook_credentials import resolve_facebook_credentials
    from shorts_bot.integrations.facebook_reel_api import probe_facebook_reel_api

    pid, token, source = resolve_facebook_credentials()
    if not pid or not token:
        return False, "No Facebook API credentials (env or data/facebook_api.json)"
    ok, detail = probe_facebook_reel_api(page_id=pid, access_token=token)
    return ok, f"{detail} (source={source})"
