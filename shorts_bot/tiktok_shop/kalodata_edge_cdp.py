"""Attach Playwright to owner Edge session via CDP — reuse Kalodata login, no Cloudflare cold start."""

from __future__ import annotations

import logging
import os
from typing import Any

from shorts_bot.config import settings

logger = logging.getLogger(__name__)

DEFAULT_CDP = "http://127.0.0.1:9222"


def cdp_url() -> str:
    raw = (
        (os.environ.get("KALODATA_EDGE_CDP_URL") or "").strip()
        or (getattr(settings, "kalodata_edge_cdp_url", None) or "")
        or DEFAULT_CDP
    )
    return raw.rstrip("/")


def cdp_enabled() -> bool:
    """When not explicitly off, try CDP once — falls back to Playwright profile on failure."""
    flag = (os.environ.get("KALODATA_EDGE_CDP") or "auto").strip().lower()
    if flag in ("0", "false", "no"):
        return False
    return True


def connect_cdp_page(playwright):
    """Return (browser, context, page) attached to Edge. Caller must NOT close browser."""
    url = cdp_url()
    browser = playwright.chromium.connect_over_cdp(url)
    if not browser.contexts:
        raise RuntimeError(f"Edge CDP connected but no contexts at {url}")
    context = browser.contexts[0]
    page = find_kalodata_page(context)
    if page is None:
        page = context.new_page()
    return browser, context, page


def find_kalodata_page(context) -> Any | None:
    for page in context.pages:
        try:
            if "kalodata.com" in (page.url or "").lower():
                return page
        except Exception:
            continue
    return None


def hub_edge_debug_command() -> str:
    """Windows command to start Edge with remote debugging (owner runs once per boot if needed)."""
    return (
        'cmd.exe /c start "" msedge --remote-debugging-port=9222 '
        "https://www.kalodata.com/product"
    )
