"""Probe TurboScribe login / Cloudflare without uploading audio."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from enum import Enum


class TurboScribeState(str, Enum):
    OK = "ok"
    NOT_LOGGED_IN = "not_logged_in"
    CLOUDFLARE = "cloudflare"
    PROFILE_LOCKED = "profile_locked"
    ERROR = "error"


@dataclass
class TurboScribeProbe:
    state: TurboScribeState
    detail: str
    file_inputs: int = 0
    action: str | None = None


def probe_turboscribe(*, timeout_sec: int = 90) -> TurboScribeProbe:
    """Check TurboScribe session. Uses visible browser when DISPLAY is set."""
    from shorts_bot.browser.profile_lock import browser_profile_locked

    locked, lock_detail = browser_profile_locked()
    if locked:
        return TurboScribeProbe(
            TurboScribeState.PROFILE_LOCKED,
            lock_detail,
            action="Close Desktop browser tab, then retry",
        )

    try:
        from playwright.sync_api import sync_playwright

        from shorts_bot.browser.stealth import launch_stealth_context
    except Exception as exc:
        return TurboScribeProbe(TurboScribeState.ERROR, str(exc)[:120])

    headless = not bool(os.environ.get("DISPLAY"))
    try:
        with sync_playwright() as p:
            context = launch_stealth_context(p, headless=headless)
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://turboscribe.ai/u", wait_until="domcontentloaded", timeout=120000)
            deadline = time.time() + timeout_sec
            while time.time() < deadline:
                body = (page.inner_text("body") or "").lower()
                if "cloudflare" in body or "security verification" in body or "ray id" in body:
                    time.sleep(4)
                    continue
                break
            else:
                context.close()
                return TurboScribeProbe(
                    TurboScribeState.CLOUDFLARE,
                    "Cloudflare blocks automated browser — export transcript on Desktop",
                    action="python3 -m shorts_bot.production.turboscribe_handoff_cli --draft-id N",
                )

            body = (page.inner_text("body") or "").lower()
            files = page.locator('input[type="file"]').count()
            context.close()

            if "sign in" in body or "log in" in body:
                return TurboScribeProbe(
                    TurboScribeState.NOT_LOGGED_IN,
                    "Not signed in",
                    file_inputs=files,
                    action="python3 -m shorts_bot.login_handoff --only turboscribe",
                )
            if files == 0 and "upload" not in body:
                return TurboScribeProbe(
                    TurboScribeState.CLOUDFLARE,
                    "TurboScribe UI not reachable (likely bot check)",
                    action="python3 -m shorts_bot.production.turboscribe_handoff_cli --draft-id N",
                )
            return TurboScribeProbe(
                TurboScribeState.OK,
                f"Logged in — {files} upload control(s)",
                file_inputs=files,
            )
    except Exception as exc:
        msg = str(exc)
        if "existing browser session" in msg.lower():
            return TurboScribeProbe(
                TurboScribeState.PROFILE_LOCKED,
                "Profile locked by another Chromium session",
                action="Close Desktop browser tab",
            )
        return TurboScribeProbe(TurboScribeState.ERROR, msg[:120])


def turboscribe_ready() -> tuple[bool, str]:
    probe = probe_turboscribe(timeout_sec=45 if os.environ.get("DISPLAY") else 20)
    if probe.state == TurboScribeState.OK:
        return True, probe.detail
    return False, probe.detail
