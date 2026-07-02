"""Stealth Chromium launch — reduces Google 'browser not secure' blocks."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.config import settings

CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

_STEALTH_ARGS = (
    "--start-maximized",
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--no-first-run",
    "--no-default-browser-check",
)

_STEALTH_INIT = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
window.chrome = window.chrome || { runtime: {} };
"""


def launch_stealth_context(
    playwright,
    *,
    headless: bool = False,
    profile_dir: Path | None = None,
    channel: str | None = None,
):
    """Persistent context with automation flags stripped (Google sign-in friendly)."""
    profile = profile_dir or settings.browser_profile_dir
    profile.mkdir(parents=True, exist_ok=True)
    launch_kwargs: dict = dict(
        user_data_dir=str(profile),
        headless=headless,
        user_agent=CHROME_UA,
        viewport={"width": 1400, "height": 900},
        accept_downloads=True,
        ignore_default_args=["--enable-automation"],
        args=list(_STEALTH_ARGS),
    )
    if channel:
        launch_kwargs["channel"] = channel
    ctx = playwright.chromium.launch_persistent_context(**launch_kwargs)
    ctx.add_init_script(_STEALTH_INIT)
    return ctx
