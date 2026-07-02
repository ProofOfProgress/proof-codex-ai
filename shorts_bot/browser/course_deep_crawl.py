"""Deep Momentum Academy crawl — BFS all internal routes (DOM, read-only)."""

from __future__ import annotations

import re
import time
from pathlib import Path
from urllib.parse import urlparse

from shorts_bot.browser.course_session import (
    _discover_internal_links,
    _ensure_logged_in_page,
    _load_course_creds,
    _profile_dir,
)
from shorts_bot.config import settings

# Known resource slugs (SPA routes not always linked until clicked)
_RESOURCE_SLUGS = (
    "faqs",
    "bof-video-examples",
    "violations-and-appeals",
    "violations-appeals",
    "how-to-grow-accounts",
    "purchase-accounts",
    "increased-commission",
    "software",
    "hire-a-va",
    "va-training",
    "make-your-own-sales-audio",
    "sales-audio",
)

_COURSE_TABS = (
    "",
    "?s=stage1",
    "?s=stage2",
    "?s=stage3",
    "?tab=strategies",
    "?tab=video-guides",
    "?tab=start-here",
    "/strategies",
    "/video-guides",
    "/start-here",
)

_EXTRA_PATHS = (
    "/program",
    "/dashboard",
    "/resources",
    "/weekly-drop",
    "/end-of-day",
    "/eod",
    "/course",
    "/mentor",
    "/product-scout",
    "/aags",
    "/appeal",
    "/video-director",
)


def _seed_urls(base: str) -> list[str]:
    seeds: list[str] = []
    for path in _EXTRA_PATHS:
        seeds.append(f"{base}{path}")
    for slug in _RESOURCE_SLUGS:
        seeds.append(f"{base}/resources/{slug}")
    for tab in _COURSE_TABS:
        seeds.append(f"{base}/course{tab}")
    return seeds


def _slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/").replace("/", "-") or "home"
    q = urlparse(url).query.replace("=", "-").replace("&", "_")
    return f"{path}-{q}" if q else path


def _extract_text(page) -> str:
    try:
        return str(page.inner_text("main", timeout=6_000))
    except Exception:
        try:
            return str(page.inner_text("body", timeout=12_000))
        except Exception:
            return ""


def deep_crawl_momentum(*, max_pages: int = 100, max_chars: int = 50_000) -> Path:
    """BFS crawl; writes combined MD + per-page snippets under inbox/momentum-deep/."""
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    email, password, base = _load_course_creds()
    profile = _profile_dir()
    profile.mkdir(parents=True, exist_ok=True)

    inbox = settings.data_dir / "research" / "course" / "inbox"
    deep_dir = inbox / "momentum-deep"
    deep_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d")
    index_path = inbox / f"momentum-deep-crawl-{stamp}.md"

    pw = sync_playwright().start()
    queue: list[str] = _seed_urls(base)
    seen: set[str] = set()
    sections: list[str] = [
        f"# Momentum Academy deep crawl — {stamp}",
        "",
        f"Pages crawled (max {max_pages}). Profile: `{profile}`",
        "",
    ]

    try:
        ctx = launch_stealth_context(pw, headless=True, profile_dir=profile)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        _ensure_logged_in_page(page, base=base, email=email, password=password)

        while queue and len(seen) < max_pages:
            url = queue.pop(0).rstrip("/")
            key = url.split("#")[0].rstrip("/")
            if key in seen:
                continue
            seen.add(key)

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=90_000)
                try:
                    page.wait_for_load_state("networkidle", timeout=8_000)
                except Exception:
                    pass
                time.sleep(1.0)
                final = page.url.split("#")[0].rstrip("/")
                title = page.title() or final
                text = _extract_text(page)
                text = re.sub(r"\n{3,}", "\n\n", text).strip()[:max_chars]

                slug = _slug_from_url(final)[:80]
                snippet = deep_dir / f"{len(seen):03d}-{slug}.md"
                snippet.write_text(
                    f"# {title}\n\nURL: {final}\n\n{text}\n",
                    encoding="utf-8",
                )

                sections.extend([f"## {title}", "", f"URL: {final}", f"File: `{snippet.name}`", ""])
                if text:
                    sections.append(text[:4000])
                    if len(text) > 4000:
                        sections.append(f"\n… ({len(text)} chars total — see `{snippet.name}`)\n")
                sections.append("")

                for link in _discover_internal_links(page, base):
                    if link.rstrip("/") not in seen and link not in queue:
                        queue.append(link)
            except Exception as exc:
                sections.extend([f"## {url}", "", f"ERROR: {exc}", ""])

        ctx.close()
    finally:
        pw.stop()

    sections.append(f"\n---\n**Total pages:** {len(seen)}\n")
    index_path.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    return index_path
