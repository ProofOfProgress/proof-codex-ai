"""Attach Playwright to owner Edge session via CDP — reuse Kalodata login, no Cloudflare cold start."""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from typing import Any

from shorts_bot.config import settings

logger = logging.getLogger(__name__)

DEFAULT_CDP = "http://127.0.0.1:9222"


def _wsl_windows_host() -> str | None:
    """WSL2: Edge debug port listens on Windows host, not Linux localhost."""
    try:
        if "microsoft" not in Path("/proc/version").read_text(encoding="utf-8", errors="ignore").lower():
            return None
    except OSError:
        return None
    try:
        for line in Path("/etc/resolv.conf").read_text(encoding="utf-8").splitlines():
            if line.startswith("nameserver"):
                return line.split()[1].strip()
    except Exception:
        pass
    try:
        out = subprocess.check_output(["ip", "route", "show", "default"], text=True, timeout=3)
        return out.split()[2]
    except Exception:
        return None


def cdp_url() -> str:
    raw = (
        (os.environ.get("KALODATA_EDGE_CDP_URL") or "").strip()
        or (getattr(settings, "kalodata_edge_cdp_url", None) or "")
    ).strip()
    if raw:
        return raw.rstrip("/")
    host = _wsl_windows_host()
    if host:
        return f"http://{host}:9222"
    return DEFAULT_CDP.rstrip("/")


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
    """Windows: Edge with CDP reachable from WSL (bind all interfaces)."""
    return (
        'powershell.exe -NoProfile -Command "Start-Process msedge -ArgumentList '
        "'--remote-debugging-port=9222','--remote-debugging-address=0.0.0.0',"
        "'https://www.kalodata.com/product'" + '"'
    )
