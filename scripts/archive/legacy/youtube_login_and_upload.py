#!/usr/bin/env python3
"""Open Google sign-in on Desktop (stealth browser), wait, then upload draft."""

from __future__ import annotations

import argparse
import sys
import time

from playwright.sync_api import sync_playwright

from shorts_bot.browser.session import _SITE_URLS
from shorts_bot.browser.stealth import launch_stealth_context
from shorts_bot.config import settings
from shorts_bot.youtube.studio import open_studio
from shorts_bot.youtube.studio_upload import (
    _perform_studio_upload_on_page,
    _preflight_studio_upload,
    _resolve_upload_fields,
)


def _studio_ready(page) -> bool:
    if "accounts.google.com" in page.url:
        return False
    status = open_studio(page)
    return status.logged_in and status.in_studio


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft-id", type=int, default=3)
    parser.add_argument("--wait-minutes", type=int, default=30)
    parser.add_argument(
        "--login-only",
        action="store_true",
        help="Open sign-in and wait — do not upload",
    )
    args = parser.parse_args()

    pack = settings.data_dir / "production" / f"draft_{args.draft_id}"
    video = pack / "final_short.mp4"
    if not args.login_only and not video.exists():
        print(f"Missing {video}", file=sys.stderr, flush=True)
        return 1

    if not args.login_only:
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

    print(
        "Opening Google sign-in on Desktop (stealth browser).\n"
        "Type your email + password yourself — do not use app passwords.\n"
        "After Google login, open the YouTube Studio tab and confirm channel.",
        flush=True,
    )

    with sync_playwright() as p:
        ctx = launch_stealth_context(p, headless=False)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(_SITE_URLS["google"], wait_until="domcontentloaded", timeout=120000)
        studio = ctx.new_page()
        studio.goto(_SITE_URLS["youtube"], wait_until="domcontentloaded", timeout=120000)

        deadline = time.time() + args.wait_minutes * 60
        while time.time() < deadline:
            if _studio_ready(studio):
                print("YouTube Studio login detected.", flush=True)
                break
            time.sleep(5)
        else:
            print("Login timeout — still not in Studio.", file=sys.stderr, flush=True)
            ctx.close()
            return 2

        if args.login_only:
            ctx.close()
            print("Login saved in browser profile.", flush=True)
            return 0

        print("Uploading final_short.mp4 …", flush=True)
        result = _perform_studio_upload_on_page(
            studio,
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
