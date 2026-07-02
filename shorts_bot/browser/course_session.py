"""Momentum Academy — Playwright login + page crawl (DOM, not vision)."""

from __future__ import annotations

import os
import re
import time
from pathlib import Path

from shorts_bot.config import settings


def _profile_dir() -> Path:
    return settings.browser_profile_dir / "momentum_academy"


def _load_course_creds() -> tuple[str, str, str]:
    """Email, password, base URL from env or gitignored agent_credentials.env."""
    cred_path = settings.data_dir / "agent_credentials.env"
    if cred_path.is_file():
        for line in cred_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            if val and key not in os.environ:
                os.environ[key] = val

    url = (
        (os.environ.get("COURSE_SITE_URL") or settings.course_site_url or "")
        .strip()
        or "https://app.momentumacademy.co"
    ).rstrip("/")
    email = (os.environ.get("COURSE_LOGIN_EMAIL") or "").strip()
    password = (os.environ.get("COURSE_LOGIN_PASSWORD") or "").strip()
    if not email or not password:
        raise RuntimeError(
            "Course login not configured — set COURSE_LOGIN_EMAIL + COURSE_LOGIN_PASSWORD "
            f"in {cred_path} or Cursor secrets (new agent run)"
        )
    return email, password, url


def _logged_in(page) -> bool:
    body = (page.inner_text("body") or "").lower()
    if "sign out" in body or "log out" in body or "welcome back" in body:
        return True
    if "sign in" in body and "credentials" in body:
        return False
    return "momentum academy" in body and "dashboard" in body


def login_and_save_session(*, headless: bool = True) -> Path:
    """Log into Momentum Academy; persistent profile for future crawls."""
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    email, password, base = _load_course_creds()
    login_url = f"{base}/login?v=1" if "/login" not in base else base
    profile = _profile_dir()
    profile.mkdir(parents=True, exist_ok=True)

    pw = sync_playwright().start()
    try:
        ctx = launch_stealth_context(pw, headless=headless, profile_dir=profile)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(login_url, wait_until="domcontentloaded", timeout=120_000)
        time.sleep(2)

        # DOM selectors — no screenshot vision
        for sel in (
            'input[type="email"]',
            'input[name="email"]',
            'input[placeholder*="email" i]',
            'input[autocomplete="email"]',
        ):
            if page.locator(sel).count():
                page.locator(sel).first.fill(email)
                break
        for sel in (
            'input[type="password"]',
            'input[name="password"]',
        ):
            if page.locator(sel).count():
                page.locator(sel).first.fill(password)
                break
        for sel in (
            'button:has-text("Sign in")',
            'button[type="submit"]',
            'input[type="submit"]',
        ):
            if page.locator(sel).count():
                page.locator(sel).first.click()
                break
        page.wait_for_load_state("domcontentloaded", timeout=60_000)
        time.sleep(3)

        if not _logged_in(page):
            raise RuntimeError("Momentum Academy login may have failed — still on sign-in page")

        ctx.close()
    finally:
        pw.stop()
    return profile


def crawl_visible_text(*, max_chars: int = 50_000) -> str:
    """Return main page text from logged-in session."""
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    _, _, base = _load_course_creds()
    profile = _profile_dir()
    if not profile.is_dir():
        login_and_save_session()

    pw = sync_playwright().start()
    try:
        ctx = launch_stealth_context(pw, headless=True, profile_dir=profile)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(base, wait_until="domcontentloaded", timeout=120_000)
        time.sleep(2)
        text = page.inner_text("main") or page.inner_text("body") or ""
        ctx.close()
    finally:
        pw.stop()
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text[:max_chars]


def _ensure_logged_in_page(page, *, base: str, email: str, password: str) -> None:
    page.goto(base, wait_until="domcontentloaded", timeout=120_000)
    time.sleep(2)
    if _logged_in(page):
        return
    page.goto(f"{base}/login?v=1", wait_until="domcontentloaded", timeout=120_000)
    time.sleep(1)
    if page.locator('input[type="email"]').count():
        page.locator('input[type="email"]').first.fill(email)
        page.locator('input[type="password"]').first.fill(password)
        page.locator('button:has-text("Sign in")').first.click()
        page.wait_for_load_state("domcontentloaded", timeout=60_000)
        time.sleep(2)
    if not _logged_in(page):
        raise RuntimeError("Momentum Academy session expired — re-run hub_course_login.sh")


def _discover_internal_links(page, base: str) -> list[str]:
    hrefs: list[str] = page.evaluate(
        """() => Array.from(document.querySelectorAll('a[href]'))
        .map(a => a.href).filter(Boolean)"""
    )
    base_host = base.replace("https://", "").replace("http://", "").split("/")[0]
    seen: set[str] = set()
    out: list[str] = []
    for href in hrefs:
        if base_host not in href:
            continue
        clean = href.split("#")[0].rstrip("/")
        if clean in seen or "/login" in clean:
            continue
        seen.add(clean)
        out.append(clean)
    return out


# Nav labels worth crawling even if link discovery misses them
_PRIORITY_PATHS = (
    "",
    "/program",
    "/resources",
    "/dashboard",
    "/end-of-day",
    "/weekly-drop",
)


def crawl_course_site(*, max_pages: int = 25, max_chars: int = 30_000) -> Path:
    """
    Crawl Momentum Academy with saved Playwright profile (DOM text, read-only).
    Writes data/research/course/inbox/momentum-crawl-YYYY-MM-DD.md
    """
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    email, password, base = _load_course_creds()
    profile = _profile_dir()
    profile.mkdir(parents=True, exist_ok=True)

    inbox = settings.data_dir / "research" / "course" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d")
    out_path = inbox / f"momentum-crawl-{stamp}.md"

    pw = sync_playwright().start()
    sections: list[str] = [
        f"# Momentum Academy crawl — {stamp}",
        "",
        f"Base: {base} · profile: `{profile}` · read-only DOM extract",
        "",
    ]
    visited: set[str] = set()

    try:
        ctx = launch_stealth_context(pw, headless=True, profile_dir=profile)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        _ensure_logged_in_page(page, base=base, email=email, password=password)

        candidates = [f"{base}{p}" if p else base for p in _PRIORITY_PATHS]
        candidates.extend(_discover_internal_links(page, base))
        # De-dupe preserve order
        ordered: list[str] = []
        for url in candidates:
            key = url.rstrip("/")
            if key not in visited:
                visited.add(key)
                ordered.append(url)

        for url in ordered[:max_pages]:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=90_000)
                time.sleep(1.5)
                title = page.title() or url
                try:
                    text = page.inner_text("main", timeout=8_000)
                except Exception:
                    text = page.inner_text("body", timeout=15_000)
                text = re.sub(r"\n{3,}", "\n\n", str(text or "")).strip()[:max_chars]
                sections.extend([f"## {title}", "", f"URL: {page.url}", ""])
                if text:
                    sections.append(text)
                else:
                    sections.append("(no text)")
                sections.append("")
            except Exception as exc:
                sections.extend([f"## {url}", "", f"ERROR: {exc}", ""])

        ctx.close()
    finally:
        pw.stop()

    out_path.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    return out_path
