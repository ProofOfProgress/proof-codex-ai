"""Unified Playwright browser session for automation and human handoff."""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from shorts_bot.config import settings

_SITE_URLS = {
    "youtube": "https://studio.youtube.com",
    "studio": "https://studio.youtube.com",
    "vidiq": "https://app.vidiq.com/auth/login",
    "turboscribe": "https://turboscribe.ai/u",
    "google": "https://accounts.google.com/signin",
    "trends": "https://trends.google.com/trends/explore",
    "capcut": "https://www.capcut.com/my-edit",
    "invideo": "https://ai.invideo.io/login",
    "discord": "https://discord.com/channels/@me",
}


def _settings_site_urls() -> dict[str, str]:
    out: dict[str, str] = {}
    if settings.course_site_url:
        out["course"] = settings.course_site_url.strip()
    if settings.course_bubble_tool_url:
        out["course-bubble"] = settings.course_bubble_tool_url.strip()
    if settings.discord_guild_id and settings.discord_channel_ids:
        first = settings.discord_channel_ids.split(",")[0].strip()
        if first:
            out["discord-channel"] = f"https://discord.com/channels/{settings.discord_guild_id.strip()}/{first}"
    return out


@dataclass
class BrowseResult:
    url: str
    title: str
    text: str
    screenshot_path: str | None = None
    logged_in_hint: str | None = None
    message: str = ""

    def summary(self, *, max_chars: int = 3500) -> str:
        lines = [f"**{self.title or 'Page'}**", self.url]
        if self.logged_in_hint:
            lines.append(f"Session: {self.logged_in_hint}")
        if self.message:
            lines.append(self.message)
        if self.text:
            lines.append("")
            lines.append(self.text[:max_chars])
        if self.screenshot_path:
            lines.append(f"\nScreenshot: `{self.screenshot_path}`")
        return "\n".join(lines)


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def resolve_url(url_or_site: str) -> str:
    key = url_or_site.strip().lower()
    if key in _SITE_URLS:
        return _SITE_URLS[key]
    extra = _settings_site_urls()
    if key in extra:
        return extra[key]
    u = url_or_site.strip()
    if u.startswith("http://") or u.startswith("https://"):
        return u
    if "." in u:
        return f"https://{u}"
    raise ValueError(f"Unknown site or URL: {url_or_site}")


def is_playwright_ready() -> tuple[bool, str]:
    if not settings.browser_enabled:
        return False, "Browser disabled (BROWSER_ENABLED=false)"
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        profile = settings.browser_profile_dir
        return True, f"Chromium OK — profile `{profile}`"
    except Exception as exc:
        return False, f"{exc} — run: python3 -m playwright install chromium"


def _strip_html(html: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _login_hint(body: str) -> str | None:
    lower = body.lower()
    if "sign out" in lower or "log out" in lower:
        return "logged in"
    if "sign in" in lower or "log in" in lower:
        return "not logged in"
    return None


def _launch_context(*, headless: bool | None = None):
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    use_headless = settings.browser_headless if headless is None else headless
    if not use_headless and not _has_display():
        use_headless = True

    pw = sync_playwright().start()
    context = launch_stealth_context(pw, headless=use_headless)
    return pw, context


def browse_url(
    url_or_site: str,
    *,
    wait_sec: float = 2.5,
    max_chars: int = 8000,
    screenshot: bool = False,
    headless: bool | None = None,
) -> BrowseResult:
    """Navigate with saved browser profile and return page text."""
    if not settings.browser_enabled:
        raise RuntimeError("Browser disabled. Set BROWSER_ENABLED=true in .env")

    url = resolve_url(url_or_site)
    pw, context = _launch_context(headless=headless)
    shot_path: str | None = None
    try:
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=120000)
        time.sleep(wait_sec)
        title = page.title() or ""
        try:
            text = page.inner_text("main") or page.inner_text("body") or ""
        except Exception:
            text = _strip_html(page.content())
        text = re.sub(r"\n{3,}", "\n\n", text).strip()[:max_chars]
        body_lower = text.lower()
        hint = _login_hint(body_lower)

        if screenshot or settings.browser_save_screenshots:
            settings.browser_screenshot_dir.mkdir(parents=True, exist_ok=True)
            host = urlparse(url).netloc.replace(".", "_")[:40] or "page"
            shot = settings.browser_screenshot_dir / f"browse_{host}_{int(time.time())}.png"
            page.screenshot(path=str(shot), full_page=False)
            shot_path = str(shot)

        return BrowseResult(
            url=page.url,
            title=title,
            text=text,
            screenshot_path=shot_path,
            logged_in_hint=hint,
        )
    finally:
        context.close()
        pw.stop()


def open_browser_for_human(
    url_or_site: str,
    *,
    minutes: int | None = None,
    block: bool = False,
) -> BrowseResult:
    """Open a visible browser tab for human control (Desktop pane)."""
    if not settings.browser_enabled:
        raise RuntimeError("Browser disabled. Set BROWSER_ENABLED=true in .env")
    if not settings.browser_allow_visible:
        raise RuntimeError("Visible browser disabled. Set BROWSER_ALLOW_VISIBLE=true")

    url = resolve_url(url_or_site)
    mins = minutes or settings.browser_open_minutes

    if not block:
        if not _has_display():
            result = browse_url(url, headless=True, max_chars=2000)
            result.message = (
                "No display — headless browse only. "
                "Open Cursor Desktop pane, then: "
                f"`python3 -m shorts_bot.browser.cli open {url_or_site}`"
            )
            return result
        msg = spawn_visible_browser(url_or_site, minutes=mins)
        return BrowseResult(url=url, title="", text="", message=msg)

    pw, context = _launch_context(headless=False)
    try:
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=120000)
        title = page.title() or url
        time.sleep(mins * 60)
        return BrowseResult(
            url=page.url,
            title=title,
            text="",
            message=f"Browser was open for {mins} min — you had control.",
        )
    finally:
        context.close()
        pw.stop()


def spawn_visible_browser(url_or_site: str, *, minutes: int | None = None) -> str:
    """Background visible browser (non-blocking for chat handlers)."""
    import subprocess
    import sys

    url = resolve_url(url_or_site)
    mins = minutes or settings.browser_open_minutes
    cmd = [
        sys.executable,
        "-m",
        "shorts_bot.browser.cli",
        "open",
        url,
        "--minutes",
        str(mins),
        "--block",
    ]
    subprocess.Popen(cmd, start_new_session=True)  # noqa: S603
    return f"Opening browser on Desktop: {url} ({mins} min)"


def fetch_page_text(url: str, *, max_chars: int = 600) -> str:
    """Best-effort page text for deep research — headless, swallow errors."""
    if not settings.browser_enabled or not settings.browser_use_for_research:
        return ""
    try:
        result = browse_url(url, max_chars=max_chars, wait_sec=2.0, screenshot=False)
        return result.text
    except Exception:
        return ""
