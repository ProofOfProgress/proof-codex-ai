"""Facebook account + Page setup via Google sign-in (saved browser profile)."""

from __future__ import annotations

import argparse
import time

from rich.console import Console

console = Console()


def signup_facebook_with_google(*, wait_seconds: int = 120) -> str:
    """Click Continue with Google → pick visible account. Returns status message."""
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    with sync_playwright() as p:
        context = launch_stealth_context(p, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.facebook.com/r.php", wait_until="domcontentloaded", timeout=120000)
        time.sleep(3)

        # Already logged in?
        if "facebook.com/home" in page.url or page.locator('[aria-label="Your profile"]').count():
            context.close()
            return "Already logged into Facebook."

        for label in (
            "Continue with Google",
            "Log in with Google",
            "Sign in with Google",
            "Google",
        ):
            try:
                btn = page.get_by_role("button", name=label)
                if btn.count():
                    btn.first.click(timeout=8000)
                    break
                link = page.get_by_text(label, exact=False)
                if link.count():
                    link.first.click(timeout=8000)
                    break
            except Exception:
                continue

        time.sleep(4)

        # Google account chooser — click first / only account
        for sel in (
            '[data-email]',
            'div[data-identifier]',
            '[role="link"]:has-text("@")',
            'li:has(div[data-email])',
        ):
            try:
                loc = page.locator(sel)
                if loc.count():
                    loc.first.click(timeout=10000)
                    break
            except Exception:
                continue
        else:
            try:
                page.get_by_text("@", exact=False).first.click(timeout=8000)
            except Exception:
                pass

        time.sleep(wait_seconds)

        url = page.url
        body = (page.inner_text("body") or "").lower()
        context.close()

        if "checkpoint" in url or "confirm" in body:
            return "Facebook needs manual verification (2FA/checkpoint) — finish in Desktop browser."
        if "facebook.com" in url and "r.php" not in url:
            return f"Facebook signup/login likely complete — landed on {url}"
        return f"Facebook flow incomplete — check Desktop browser (url={url})"


def main() -> None:
    parser = argparse.ArgumentParser(description="Facebook signup via Google")
    parser.add_argument("--wait", type=int, default=120, help="Seconds to wait after account click")
    args = parser.parse_args()
    msg = signup_facebook_with_google(wait_seconds=args.wait)
    console.print(msg)


if __name__ == "__main__":
    main()
