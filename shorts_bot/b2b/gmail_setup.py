"""Create dedicated Gmail for B2B outreach (browser + human phone step)."""

from __future__ import annotations

import json
import re
import secrets
import string
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

from shorts_bot.config import settings

SetupStatus = Literal["started", "needs_human", "created", "failed"]

GOOGLE_SIGNUP = (
    "https://accounts.google.com/signup/v2/createaccount"
    "?flowName=GlifWebSignIn&flowEntry=SignUp"
)

HUMAN_KEYWORDS = (
    "verify",
    "captcha",
    "challenge",
    "phone",
    "sms",
    "confirm you're not a robot",
    "security check",
    "qr code",
    "could not create",
)


@dataclass
class GmailSetupResult:
    status: SetupStatus
    message: str
    email: str = ""
    password: str = ""
    screenshot_path: str = ""
    current_url: str = ""
    handoff_path: str = ""


def _profile_dir() -> Path:
    return settings.data_dir / "browser_profile_b2b_outreach"


def _handoff_path() -> Path:
    return settings.data_dir / "b2b" / "gmail_setup_handoff.json"


def _generate_password(length: int = 20) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    while True:
        pwd = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in pwd)
            and any(c.isupper() for c in pwd)
            and any(c.isdigit() for c in pwd)
        ):
            return pwd


def _username_candidates() -> list[str]:
    suffix = secrets.token_hex(3)
    return [
        f"rtr.outreach.{suffix}",
        f"rapidtoolreview.outreach.{suffix}",
        f"rtroutreach.{suffix}",
        f"msbyte.outreach.{suffix}",
    ]


def _screenshot(page, label: str) -> str:
    out = settings.browser_screenshot_dir / f"b2b_gmail_{label}_{int(time.time())}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        page.screenshot(path=str(out), full_page=True)
        return str(out)
    except Exception:
        return ""


def _page_text(page) -> str:
    try:
        return (page.inner_text("body") or "").lower()
    except Exception:
        return ""


def _needs_human(page) -> bool:
    blob = f"{_page_text(page)} {page.url.lower()}"
    return any(k in blob for k in HUMAN_KEYWORDS)


def _click_next(page) -> None:
    for label in ("Next", "I agree", "Create account"):
        try:
            page.get_by_role("button", name=re.compile(f"^{label}$", re.I)).click(timeout=5000)
            return
        except Exception:
            continue


def _fill_name(page, first_name: str, last_name: str) -> None:
    page.locator('input[name="firstName"]').fill(first_name)
    page.locator('input[name="lastName"]').fill(last_name)
    _click_next(page)
    time.sleep(2)


def _fill_birthday(page, birth_date: date) -> None:
    page.locator("#month").click()
    time.sleep(0.4)
    month_name = birth_date.strftime("%B")
    page.get_by_role("option", name=month_name).click()
    page.locator("#day").fill(str(birth_date.day))
    page.locator("#year").fill(str(birth_date.year))
    page.locator("#gender").click()
    time.sleep(0.4)
    page.get_by_role("option", name="Rather not say").click()
    _click_next(page)
    time.sleep(2)


def _pick_username(page, candidates: list[str]) -> str:
    taken = re.compile(r"not available|already taken|try another|choose another", re.I)
    page.get_by_text("Create your own Gmail address").click()
    time.sleep(0.8)
    field = page.locator('input[name="Username"]')
    for candidate in candidates:
        field.fill(candidate)
        time.sleep(0.8)
        _click_next(page)
        time.sleep(2)
        if not taken.search(_page_text(page)):
            return f"{candidate}@gmail.com"
        # go back to username step if possible
        try:
            page.go_back()
            time.sleep(1.5)
            page.get_by_text("Create your own Gmail address").click()
            time.sleep(0.8)
        except Exception:
            pass
    return ""


def _fill_password(page, password: str) -> None:
    fields = page.locator('input[type="password"]')
    fields.nth(0).fill(password)
    if fields.count() >= 2:
        fields.nth(1).fill(password)
    _click_next(page)
    time.sleep(2)


def _write_handoff(*, email: str, password: str, status: str, message: str) -> Path:
    path = _handoff_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": status,
        "email": email,
        "password": password,
        "message": message,
        "secrets_to_add": {
            "B2B_SMTP_USER": email,
            "B2B_SMTP_APP_PASSWORD": "(Google App Password — create after account is live)",
            "B2B_TEST_EMAIL": "(your personal inbox for test pings)",
            "B2B_EMAIL_FROM_NAME": "Kim",
        },
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


class B2BGmailSetup:
    def __init__(self, *, headless: bool = False, wait_minutes: int = 25) -> None:
        self.headless = headless
        self.wait_minutes = wait_minutes

    def run(
        self,
        *,
        first_name: str = "Kim",
        last_name: str = "RTR Outreach",
        birth_date: date | None = None,
    ) -> GmailSetupResult:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return GmailSetupResult(status="failed", message="Playwright not installed.")

        bd = birth_date or date(1990, 3, 15)
        password = _generate_password()
        chosen_email = ""
        keep_open = False

        with sync_playwright() as p:
            from shorts_bot.browser.stealth import launch_stealth_context

            context = launch_stealth_context(
                p,
                headless=self.headless,
                profile_dir=_profile_dir(),
            )
            page = context.pages[0] if context.pages else context.new_page()

            try:
                page.goto(GOOGLE_SIGNUP, wait_until="domcontentloaded", timeout=90000)
                time.sleep(2)
                _fill_name(page, first_name, last_name)

                if _needs_human(page):
                    keep_open = True
                    return self._human_stop(page, "Complete signup from this step.", password)

                _fill_birthday(page, bd)
                if _needs_human(page):
                    keep_open = True
                    return self._human_stop(page, "Complete birthday or verification.", password)

                chosen_email = _pick_username(page, _username_candidates())
                if not chosen_email:
                    keep_open = True
                    return GmailSetupResult(
                        status="needs_human",
                        message="Pick a Gmail address manually in the Desktop browser.",
                        password=password,
                        screenshot_path=_screenshot(page, "pick_username"),
                        current_url=page.url,
                    )

                if "password" not in page.url:
                    _click_next(page)
                    time.sleep(2)

                _fill_password(page, password)

                if _needs_human(page) or "could not create" in _page_text(page):
                    keep_open = True
                    handoff = _write_handoff(
                        email=chosen_email,
                        password=password,
                        status="needs_human",
                        message="Google blocked or needs phone — finish in browser.",
                    )
                    return GmailSetupResult(
                        status="needs_human",
                        message=(
                            f"Finish signup for {chosen_email} in the Desktop browser. "
                            "Google will ask for your phone — enter the code when it texts you."
                        ),
                        email=chosen_email,
                        password=password,
                        screenshot_path=_screenshot(page, "phone_or_block"),
                        current_url=page.url,
                        handoff_path=str(handoff),
                    )

                deadline = time.time() + self.wait_minutes * 60
                while time.time() < deadline:
                    if "myaccount.google.com" in page.url or "mail.google.com" in page.url:
                        handoff = _write_handoff(
                            email=chosen_email,
                            password=password,
                            status="created",
                            message="Gmail account created.",
                        )
                        return GmailSetupResult(
                            status="created",
                            message=f"Gmail ready: {chosen_email}. Create App Password → B2B_SMTP_* secrets.",
                            email=chosen_email,
                            password=password,
                            handoff_path=str(handoff),
                            screenshot_path=_screenshot(page, "done"),
                            current_url=page.url,
                        )
                    if _needs_human(page):
                        keep_open = True
                        handoff = _write_handoff(
                            email=chosen_email,
                            password=password,
                            status="needs_human",
                            message="Phone verification in progress.",
                        )
                        return GmailSetupResult(
                            status="needs_human",
                            message=f"Enter phone code for {chosen_email} in Desktop browser.",
                            email=chosen_email,
                            password=password,
                            handoff_path=str(handoff),
                            screenshot_path=_screenshot(page, "waiting_phone"),
                            current_url=page.url,
                        )
                    time.sleep(3)

                handoff = _write_handoff(
                    email=chosen_email,
                    password=password,
                    status="needs_human",
                    message="Timed out — finish in browser.",
                )
                keep_open = True
                return GmailSetupResult(
                    status="needs_human",
                    message=f"Browser stayed open {self.wait_minutes} min — finish {chosen_email} if needed.",
                    email=chosen_email,
                    password=password,
                    handoff_path=str(handoff),
                    screenshot_path=_screenshot(page, "timeout"),
                    current_url=page.url,
                )
            finally:
                if keep_open and not self.headless:
                    time.sleep(self.wait_minutes * 60)
                context.close()

    def _human_stop(self, page, msg: str, password: str, email: str = "") -> GmailSetupResult:
        handoff = _write_handoff(email=email, password=password, status="needs_human", message=msg)
        return GmailSetupResult(
            status="needs_human",
            message=msg,
            email=email,
            password=password,
            screenshot_path=_screenshot(page, "human"),
            current_url=page.url,
            handoff_path=str(handoff),
        )
