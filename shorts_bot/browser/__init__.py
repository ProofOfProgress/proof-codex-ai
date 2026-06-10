"""Playwright browser automation — shared by Discord bot, agent tools, and deep research."""

from shorts_bot.browser.session import (
    BrowseResult,
    browse_url,
    is_playwright_ready,
    open_browser_for_human,
)

__all__ = ["BrowseResult", "browse_url", "is_playwright_ready", "open_browser_for_human"]
