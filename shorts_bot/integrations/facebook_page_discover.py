"""Discover Facebook Pages from saved browser session."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass


@dataclass
class FacebookPageInfo:
    page_id: str
    name: str
    url: str = ""


def discover_managed_pages(*, timeout_sec: int = 60) -> tuple[list[FacebookPageInfo], str]:
    """
    Scrape facebook.com/pages for Page IDs when browser profile is available.
    Returns (pages, message).
    """
    from shorts_bot.browser.profile_lock import browser_profile_locked

    locked, detail = browser_profile_locked()
    if locked:
        return [], f"Browser profile locked — {detail}"

    import os

    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    headless = not bool(os.environ.get("DISPLAY"))
    pages: list[FacebookPageInfo] = []
    try:
        with sync_playwright() as p:
            context = launch_stealth_context(p, headless=headless)
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(
                "https://www.facebook.com/pages/?category=your_pages",
                wait_until="domcontentloaded",
                timeout=120000,
            )
            time.sleep(min(8, max(3, timeout_sec // 8)))
            html = page.content()
            body = page.inner_text("body") or ""

            if "sign in" in body.lower() or "log in" in body.lower()[:300]:
                context.close()
                return [], "Facebook not signed in — run login_handoff --only facebook"

            id_to_name: dict[str, str] = {}
            for match in re.finditer(r'"page_id":"(\d+)"[^}]*"name":"([^"]+)"', html):
                id_to_name[match.group(1)] = match.group(2)
            for match in re.finditer(r'"entity_id":"(\d{8,})"[^}]*"title":"([^"]+)"', html):
                id_to_name.setdefault(match.group(1), match.group(2))

            if not id_to_name and "pages you manage" in body.lower():
                managed = body.lower().split("pages you manage", 1)[-1]
                candidates = []
                for line in managed.splitlines():
                    line = line.strip()
                    if not line or line.lower() in {
                        "create page",
                        "meta business suite",
                        "discover",
                        "followed pages",
                        "invites",
                    }:
                        continue
                    if re.fullmatch(r"\d+\s+notification", line.lower()):
                        continue
                    if line.lower() in {"messages", "create post", "promote", "notifications"}:
                        continue
                    candidates.append(line)
                for name in candidates[:3]:
                    try:
                        link = page.get_by_role("link", name=re.compile(re.escape(name[:48]), re.I))
                        if not link.count():
                            link = page.get_by_text(name, exact=False)
                        if not link.count():
                            continue
                        href = link.first.get_attribute("href") or ""
                        m = re.search(r"/(\d{8,})", href)
                        if m:
                            id_to_name[m.group(1)] = name
                            continue
                        link.first.click(timeout=8000)
                        time.sleep(4)
                        url = page.url
                        m = re.search(r"facebook\.com/(?:profile\.php\?id=)?(\d{8,})", url)
                        if m:
                            id_to_name[m.group(1)] = name
                        else:
                            m2 = re.search(r'"pageID":"(\d+)"', page.content())
                            if m2:
                                id_to_name[m2.group(1)] = name
                        page.goto(
                            "https://www.facebook.com/pages/?category=your_pages",
                            wait_until="domcontentloaded",
                            timeout=120000,
                        )
                        time.sleep(2)
                    except Exception:
                        continue

            context.close()

        for pid, name in id_to_name.items():
            if name.lower() in {"messages", "create post", "promote", "notifications"}:
                continue
            pages.append(FacebookPageInfo(page_id=pid, name=name))

        if not pages:
            if "peripheral" in body.lower():
                return [], "Peripheral Page visible but ID not parsed — open Page settings → About"
            if "create page" in body.lower() or "pages you manage" in body.lower():
                return [], "Logged in but no Pages found — create Peripheral Horror Page first"
            return [], "Could not parse Page list from Facebook HTML"
        return pages, f"Found {len(pages)} managed Page(s)"
    except Exception as exc:
        msg = str(exc)
        if "existing browser session" in msg.lower():
            return [], "Browser profile locked — close Desktop browser tab"
        return [], msg[:160]
