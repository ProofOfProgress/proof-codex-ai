#!/usr/bin/env python3
"""Open YouTube Studio in visible browser, wait for login, upload draft pack."""

from __future__ import annotations

import argparse
import re
import sys
import time

from playwright.sync_api import sync_playwright

from shorts_bot.config import settings
from shorts_bot.youtube.studio import CHROME_UA, open_studio
from shorts_bot.youtube.studio_upload import (
    _perform_studio_upload_on_page,
    _preflight_studio_upload,
    _resolve_upload_fields,
)


def _fill_google_email(page, email: str) -> bool:
    try:
        box = page.locator('input[type="email"], input[name="identifier"]')
        if box.count() and box.first.is_visible():
            box.first.fill(email)
            nxt = page.get_by_role("button", name=re.compile(r"next", re.I))
            if nxt.count():
                nxt.first.click(timeout=5000)
            else:
                page.keyboard.press("Enter")
            return True
    except Exception:
        pass
    return False


def _studio_ready(page) -> bool:
    url = page.url
    if "accounts.google.com" in url:
        return False
    status = open_studio(page)
    return status.logged_in and status.in_studio


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft-id", type=int, default=3)
    parser.add_argument("--wait-minutes", type=int, default=20)
    args = parser.parse_args()

    pack = settings.data_dir / "production" / f"draft_{args.draft_id}"
    video = pack / "final_short.mp4"
    if not video.exists():
        print(f"Missing {video}", file=sys.stderr, flush=True)
        return 1

    draft_id, use_title, use_desc, use_vis = _resolve_upload_fields(
        video, title=None, description="", visibility=None, pack_dir=pack
    )
    blocked = _preflight_studio_upload(
        draft_id=draft_id,
        pack_dir=pack,
        use_title=use_title,
        allow_duplicate_draft=False,
        skip_preflight=False,
    )
    if blocked:
        print(blocked.message, file=sys.stderr, flush=True)
        return 4

    email = (settings.gmail_smtp_user or "").strip()
    profile = settings.browser_profile_dir
    profile.mkdir(parents=True, exist_ok=True)

    print("Opening YouTube Studio (visible — Desktop tab)…", flush=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(profile),
            headless=False,
            user_agent=CHROME_UA,
            viewport={"width": 1400, "height": 900},
            args=["--start-maximized"],
            accept_downloads=True,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        status = open_studio(page)
        if not status.logged_in:
            if email:
                print(f"Pre-filled Google email ({email[:3]}…). Enter password / 2FA on Desktop.", flush=True)
                _fill_google_email(page, email)
            else:
                print("Sign in on Desktop browser tab (Google → YouTube Studio).", flush=True)
            deadline = time.time() + args.wait_minutes * 60
            while time.time() < deadline:
                if _studio_ready(page):
                    print("Studio login detected.", flush=True)
                    break
                time.sleep(5)
            else:
                print("Login timeout.", file=sys.stderr, flush=True)
                ctx.close()
                return 2
        else:
            print(f"Already logged in: {status.message}", flush=True)

        print("Uploading final_short.mp4 …", flush=True)
        result = _perform_studio_upload_on_page(
            page,
            video,
            use_title=use_title,
            use_desc=use_desc,
            use_vis=use_vis,
            draft_id=draft_id,
            pack_dir=pack,
        )
        ctx.close()

    print(result.message, flush=True)
    if result.video_url:
        print(f"LIVE: {result.video_url}", flush=True)
    return 0 if result.ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
