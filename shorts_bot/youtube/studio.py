from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path

CHROME_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


@dataclass
class StudioStatus:
    logged_in: bool
    in_studio: bool
    channel_name: str | None
    message: str
    url: str


def open_studio(page) -> StudioStatus:
    """Navigate to YouTube Studio, skip browser warning if shown."""
    page.set_extra_http_headers({"User-Agent": CHROME_UA})
    page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=90000)
    time.sleep(2)
    _skip_unsupported_warning(page)
    time.sleep(2)

    url = page.url
    logged_in = "accounts.google.com" not in url
    in_studio = "studio.youtube.com" in url and "Improve your experience" not in page.title()

    name = _read_channel_name(page)
    if logged_in and in_studio:
        msg = "YouTube Studio ready."
        if name:
            msg += f" Channel: {name}."
    elif logged_in:
        msg = "Logged in but Studio not fully loaded — may need Skip to Studio."
    else:
        msg = "Not logged in."

    return StudioStatus(
        logged_in=logged_in,
        in_studio=in_studio,
        channel_name=name,
        message=msg,
        url=url,
    )


def _skip_unsupported_warning(page) -> None:
    try:
        skip = page.get_by_text(re.compile(r"skip to youtube studio", re.I))
        if skip.count() and skip.first.is_visible():
            skip.first.click(timeout=5000)
            time.sleep(2)
    except Exception:
        pass


def _read_channel_name(page) -> str | None:
    try:
        body = page.inner_text("body")
        for line in body.splitlines():
            line = line.strip()
            if line and 2 < len(line) < 80 and line not in {
                "YouTube Studio",
                "Channel dashboard",
                "Dashboard",
                "Content",
                "Analytics",
            }:
                if re.match(r"^[A-Za-z0-9 _.-]+$", line) and " " not in line[:3]:
                    continue
        # channel switcher often shows name near top
        loc = page.locator("yt-formatted-string#account-name, #channel-title")
        if loc.count():
            t = loc.first.inner_text().strip()
            if t:
                return t
    except Exception:
        pass
    return None


def check_studio(profile_dir: Path, *, headless: bool = True) -> StudioStatus:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=headless,
            user_agent=CHROME_UA,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            return open_studio(page)
        finally:
            ctx.close()
