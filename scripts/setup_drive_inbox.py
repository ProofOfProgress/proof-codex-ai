#!/usr/bin/env python3
"""One-shot setup: Google OAuth (Drive scope) + inbox folder + Drive API."""

from __future__ import annotations

import json
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOLDER_NAME = "Rapid Tool Review Inbox"
CONFIG_PATH = ROOT / "data" / "drive_inbox_config.json"
ENV_PATH = ROOT / ".env"


def _save_folder_id(folder_id: str) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps({"folder_id": folder_id, "folder_name": FOLDER_NAME}, indent=2),
        encoding="utf-8",
    )
    if ENV_PATH.exists():
        text = ENV_PATH.read_text(encoding="utf-8")
        line = f"GOOGLE_DRIVE_FOLDER_ID={folder_id}"
        if "GOOGLE_DRIVE_FOLDER_ID=" in text:
            text = re.sub(r"^GOOGLE_DRIVE_FOLDER_ID=.*$", line, text, flags=re.M)
        else:
            text = text.rstrip() + "\n" + line + "\nGOOGLE_DRIVE_INBOX_ENABLED=true\n"
        ENV_PATH.write_text(text, encoding="utf-8")


def _oauth_with_drive() -> bool:
    from shorts_bot.youtube.google_auth import auth_status, oauth_authorization_url, oauth_complete_redirect

    if auth_status().get("drive_ready"):
        return True

    captured: dict[str, str] = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args) -> None:
            pass

        def do_GET(self) -> None:
            captured["url"] = f"http://127.0.0.1:8090{self.path}"
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Connected")

    server = HTTPServer(("127.0.0.1", 8090), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    auth_url = oauth_authorization_url()
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    with sync_playwright() as p:
        context = launch_stealth_context(p, headless=True)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(auth_url, timeout=120000)
        time.sleep(2)
        try:
            page.locator("div[data-email]").first.click(timeout=5000)
            time.sleep(2)
        except Exception:
            pass
        for sel in ("button:has-text('Continue')",):
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=1500):
                    btn.click(timeout=5000)
                    time.sleep(2)
            except Exception:
                pass
        boxes = page.locator('input[type="checkbox"]')
        for i in range(boxes.count()):
            cb = boxes.nth(i)
            try:
                if not cb.is_checked():
                    cb.click(force=True, timeout=3000)
            except Exception:
                pass
        try:
            with page.expect_navigation(timeout=30000, url="http://127.0.0.1:8090/**"):
                page.locator("#submit_approve_access").click(timeout=10000)
        except Exception:
            pass
        if "url" not in captured and page.url.startswith("http://127.0.0.1:8090"):
            captured["url"] = page.url
        context.close()
    server.shutdown()

    if "url" not in captured:
        return False
    return bool(oauth_complete_redirect(captured["url"]).get("ok"))


def _enable_drive_api() -> None:
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context
    from shorts_bot.youtube.google_auth import effective_google_client_id

    cid = effective_google_client_id() or ""
    project = cid.split("-")[0] if cid else "975455641557"
    url = f"https://console.cloud.google.com/apis/library/drive.googleapis.com?project={project}"
    with sync_playwright() as p:
        context = launch_stealth_context(p, headless=True)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(url, timeout=120000)
        time.sleep(4)
        enable = page.get_by_role("button", name="Enable")
        if enable.count():
            enable.first.click(timeout=15000)
            time.sleep(6)
        context.close()


def _create_inbox_folder() -> str:
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    with sync_playwright() as p:
        context = launch_stealth_context(p, headless=True)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(
            "https://drive.google.com/drive/search?q=" + FOLDER_NAME.replace(" ", "+"),
            timeout=120000,
        )
        time.sleep(3)
        m = __import__("re").search(r"/folders/([a-zA-Z0-9_-]+)", page.url)
        if m and "search" not in page.url:
            context.close()
            return m.group(1)
        page.goto("https://drive.google.com/drive/my-drive", timeout=120000)
        time.sleep(3)
        page.get_by_role("button", name="New").click(timeout=10000)
        time.sleep(1)
        page.get_by_role("menuitem", name="New folder").click(timeout=10000)
        time.sleep(2)
        page.keyboard.type(FOLDER_NAME, delay=25)
        page.keyboard.press("Enter")
        time.sleep(4)
        page.goto(
            "https://drive.google.com/drive/search?q=" + FOLDER_NAME.replace(" ", "+"),
            timeout=120000,
        )
        time.sleep(3)
        page.get_by_text(FOLDER_NAME, exact=True).first.dblclick(timeout=10000)
        time.sleep(3)
        m = __import__("re").search(r"/folders/([a-zA-Z0-9_-]+)", page.url)
        context.close()
        if not m:
            raise RuntimeError("Could not create or find inbox folder")
        return m.group(1)


def main() -> int:
    print("Step 1/3 — Google OAuth (YouTube + Drive read)...")
    if not _oauth_with_drive():
        print("OAuth failed — open Desktop and run auth_cli connect", file=sys.stderr)
        return 1
    print("Step 2/3 — Enable Drive API in Cloud Console...")
    _enable_drive_api()
    print("Step 3/3 — Create inbox folder on Drive...")
    folder_id = _create_inbox_folder()
    _save_folder_id(folder_id)
    print(json.dumps({"ok": True, "folder_id": folder_id, "folder_name": FOLDER_NAME}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
