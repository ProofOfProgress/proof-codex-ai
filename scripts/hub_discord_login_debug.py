#!/usr/bin/env python3
"""One-off: debug Discord login state (hub)."""
from __future__ import annotations

import time
from pathlib import Path

from playwright.sync_api import sync_playwright

from shorts_bot.browser.discord_session import _discord_profile, _load_discord_creds
from shorts_bot.browser.stealth import launch_stealth_context


def main() -> None:
    email, password = _load_discord_creds()
    profile = _discord_profile()
    pw = sync_playwright().start()
    ctx = launch_stealth_context(pw, headless=True, profile_dir=profile)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://discord.com/login", timeout=120_000)
    time.sleep(2)
    page.locator('input[name="email"]').fill(email)
    page.locator('input[name="password"]').fill(password)
    page.locator('button[type="submit"]').click()
    time.sleep(10)
    out = Path("data/research/course/inbox/discord-login-debug.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    body = (page.inner_text("body") or "")[:4000]
    out.write_text(f"URL: {page.url}\n\n{body}", encoding="utf-8")
    print(out)
    print("URL:", page.url)
    ctx.close()
    pw.stop()


if __name__ == "__main__":
    main()
