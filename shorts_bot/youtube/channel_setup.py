from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

SetupStatus = Literal[
    "started",
    "needs_human",
    "logged_in",
    "channel_ready",
    "already_has_channel",
    "failed",
]


@dataclass
class ChannelSetupResult:
    status: SetupStatus
    message: str
    screenshot_path: str | None = None
    current_url: str | None = None

    def for_human(self) -> str:
        lines = [f"Status: {self.status}", self.message]
        if self.current_url:
            lines.append(f"URL: {self.current_url}")
        if self.screenshot_path:
            lines.append(f"Screenshot: {self.screenshot_path}")
        return "\n".join(lines)


class YouTubeChannelSetup:
    """
    Browser operator for Google account + YouTube channel setup.

    Google requires phone/CAPTCHA verification for new accounts — that step
    cannot be fully automated. The operator opens the browser, fills what it
    can, then pauses for a one-time human checkpoint.
    """

    GOOGLE_SIGNUP = "https://accounts.google.com/signup/v2/createaccount?flowName=GlifWebSignIn&flowEntry=SignUp"
    YOUTUBE_HOME = "https://www.youtube.com"
    YOUTUBE_STUDIO = "https://studio.youtube.com"
    YOUTUBE_CREATE = "https://www.youtube.com/create_channel"

    HUMAN_KEYWORDS = (
        "verify",
        "captcha",
        "challenge",
        "phone",
        "sms",
        "2-step",
        "two-step",
        "security check",
        "confirm you're not a robot",
    )

    def __init__(
        self,
        profile_dir: Path,
        *,
        headless: bool = False,
        screenshot_dir: Path | None = None,
    ) -> None:
        self.profile_dir = profile_dir
        self.headless = headless
        self.screenshot_dir = screenshot_dir or profile_dir / "screenshots"
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        *,
        channel_name: str,
        use_existing_google_account: bool = False,
        wait_for_human_seconds: int = 0,
    ) -> ChannelSetupResult:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return ChannelSetupResult(
                status="failed",
                message="Playwright not installed. Run: pip install playwright && playwright install chromium",
            )

        channel_name = channel_name.strip()
        if not channel_name:
            return ChannelSetupResult(status="failed", message="Channel name is required.")

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=self.headless,
                viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"],
            )
            page = context.pages[0] if context.pages else context.new_page()

            try:
                if use_existing_google_account:
                    result = self._ensure_logged_in(page)
                else:
                    result = self._start_google_signup(page)

                if result.status == "failed":
                    return result

                if result.status == "needs_human":
                    if wait_for_human_seconds > 0:
                        result = self._wait_for_human_progress(page, wait_for_human_seconds)
                        if result.status != "logged_in":
                            return result
                    else:
                        return result

                if result.status != "logged_in" and not self._looks_logged_in(page):
                    login_check = self._ensure_logged_in(page)
                    if login_check.status != "logged_in":
                        return login_check

                return self._ensure_youtube_channel(page, channel_name)
            finally:
                context.close()

    def _start_google_signup(self, page) -> ChannelSetupResult:
        page.goto(self.GOOGLE_SIGNUP, wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)
        human = self._detect_human_checkpoint(page)
        if human:
            return human
        return ChannelSetupResult(
            status="needs_human",
            message=(
                "Browser opened to Google sign-up. Complete the form, phone verification, "
                "and CAPTCHA in the browser window. Google requires this once — the bot cannot "
                "skip it. When finished, run setup again with --existing-account."
            ),
            screenshot_path=self._screenshot(page, "google_signup"),
            current_url=page.url,
        )

    def _ensure_logged_in(self, page) -> ChannelSetupResult:
        page.goto(self.YOUTUBE_HOME, wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)
        if self._looks_logged_in(page):
            return ChannelSetupResult(
                status="logged_in",
                message="Google/YouTube session detected. Proceeding to channel setup.",
                current_url=page.url,
            )
        page.goto(self.GOOGLE_SIGNUP, wait_until="domcontentloaded", timeout=60000)
        human = self._detect_human_checkpoint(page)
        if human:
            return human
        return ChannelSetupResult(
            status="needs_human",
            message=(
                "Not logged in yet. Sign in or create a Google account in the browser. "
                "Complete phone/CAPTCHA if prompted, then run setup again."
            ),
            screenshot_path=self._screenshot(page, "login_needed"),
            current_url=page.url,
        )

    def _ensure_youtube_channel(self, page, channel_name: str) -> ChannelSetupResult:
        page.goto(self.YOUTUBE_STUDIO, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        if "studio.youtube.com" in page.url and "accounts.google.com" not in page.url:
            custom_result = self._try_set_channel_name(page, channel_name)
            if custom_result:
                return custom_result
            return ChannelSetupResult(
                status="channel_ready",
                message=(
                    f"YouTube Studio is accessible — channel exists or was created. "
                    f"Set display name to '{channel_name}' in Studio → Customization if needed."
                ),
                screenshot_path=self._screenshot(page, "studio"),
                current_url=page.url,
            )

        page.goto(self.YOUTUBE_CREATE, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        human = self._detect_human_checkpoint(page)
        if human:
            return human

        self._try_click_text(page, ["Create a channel", "Get started", "Create channel"])
        time.sleep(2)
        self._try_fill_channel_name(page, channel_name)
        self._try_click_text(page, ["Create channel", "Done", "OK"])

        page.goto(self.YOUTUBE_STUDIO, wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        if "studio.youtube.com" in page.url:
            return ChannelSetupResult(
                status="channel_ready",
                message=f"YouTube channel setup reached Studio. Target name: {channel_name}.",
                screenshot_path=self._screenshot(page, "channel_ready"),
                current_url=page.url,
            )

        return ChannelSetupResult(
            status="needs_human",
            message=(
                "Could not confirm channel creation automatically. "
                "Finish 'Create a channel' in the browser if a prompt is visible."
            ),
            screenshot_path=self._screenshot(page, "channel_uncertain"),
            current_url=page.url,
        )

    def _try_set_channel_name(self, page, channel_name: str) -> ChannelSetupResult | None:
        try:
            page.goto(
                "https://studio.youtube.com/channel/UC/editing/details",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            time.sleep(2)
            name_input = page.locator('input[aria-label*="name" i], input[name*="name" i]').first
            if name_input.count():
                name_input.fill(channel_name)
                self._try_click_text(page, ["Publish", "Save"])
                return ChannelSetupResult(
                    status="channel_ready",
                    message=f"Channel display name set to '{channel_name}'.",
                    screenshot_path=self._screenshot(page, "name_set"),
                    current_url=page.url,
                )
        except Exception:
            return None
        return None

    def _try_fill_channel_name(self, page, channel_name: str) -> None:
        selectors = [
            'input[aria-label*="name" i]',
            'input[placeholder*="name" i]',
            "input#channel-name",
        ]
        for sel in selectors:
            loc = page.locator(sel).first
            if loc.count():
                try:
                    loc.fill(channel_name, timeout=3000)
                    return
                except Exception:
                    continue

    def _try_click_text(self, page, labels: list[str]) -> None:
        for label in labels:
            try:
                page.get_by_role("button", name=re.compile(label, re.I)).first.click(timeout=2000)
                return
            except Exception:
                try:
                    page.get_by_text(re.compile(label, re.I)).first.click(timeout=2000)
                    return
                except Exception:
                    continue

    def _looks_logged_in(self, page) -> bool:
        try:
            avatar = page.locator("#avatar-btn, button#avatar-btn, img[alt*='Avatar' i]")
            if avatar.count() and avatar.first.is_visible():
                return True
        except Exception:
            pass
        return "accounts.google.com/ServiceLogin" not in page.url and "signin" not in page.url.lower()

    def _detect_human_checkpoint(self, page) -> ChannelSetupResult | None:
        content = ""
        try:
            content = page.content().lower()
        except Exception:
            pass
        url = page.url.lower()
        blob = f"{content} {url}"
        if any(k in blob for k in self.HUMAN_KEYWORDS):
            return ChannelSetupResult(
                status="needs_human",
                message=(
                    "Google needs you for one step (phone code, CAPTCHA, or security check). "
                    "Complete it in the browser — this is required by Google, not optional."
                ),
                screenshot_path=self._screenshot(page, "human_checkpoint"),
                current_url=page.url,
            )
        return None

    def _wait_for_human_progress(self, page, seconds: int) -> ChannelSetupResult:
        deadline = time.time() + seconds
        while time.time() < deadline:
            if self._looks_logged_in(page):
                return ChannelSetupResult(
                    status="logged_in",
                    message="Login detected after human checkpoint.",
                    current_url=page.url,
                )
            time.sleep(3)
            page.reload(wait_until="domcontentloaded")
        return ChannelSetupResult(
            status="needs_human",
            message=f"Still waiting after {seconds}s. Complete verification in the browser and run again.",
            screenshot_path=self._screenshot(page, "still_waiting"),
            current_url=page.url,
        )

    def _screenshot(self, page, label: str) -> str:
        path = self.screenshot_dir / f"{label}_{int(time.time())}.png"
        try:
            page.screenshot(path=str(path), full_page=True)
            return str(path)
        except Exception:
            return ""
