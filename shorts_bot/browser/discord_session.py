"""Discord web intel — read-only channel text via Playwright (hub browser profile)."""

from __future__ import annotations

import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.config import settings


def _discord_profile() -> Path:
    return settings.browser_profile_dir / "discord"


def _load_discord_creds() -> tuple[str, str]:
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

    email = (os.environ.get("DISCORD_LOGIN_EMAIL") or "").strip()
    password = (os.environ.get("DISCORD_LOGIN_PASSWORD") or "").strip()
    if not email or not password:
        raise RuntimeError(
            "Discord login not configured — set DISCORD_LOGIN_EMAIL + DISCORD_LOGIN_PASSWORD "
            f"in {cred_path} (gitignored, hub only)"
        )
    return email, password


def _discord_logged_in(page) -> bool:
    url = (page.url or "").lower()
    if "/login" in url:
        return False
    body = (page.inner_text("body") or "").lower()
    if "log in" in body and "password" in body and "welcome back" in body:
        return False
    if "/channels/" in url and "login" not in url:
        return True
    return "direct messages" in body or "friends" in body


def login_discord_session(*, headless: bool = True) -> Path:
    """Log into Discord web; cookies saved in profile for future crawls."""
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    email, password = _load_discord_creds()
    profile = _discord_profile()
    profile.mkdir(parents=True, exist_ok=True)

    pw = sync_playwright().start()
    try:
        ctx = launch_stealth_context(pw, headless=headless, profile_dir=profile)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://discord.com/login", wait_until="domcontentloaded", timeout=120_000)
        time.sleep(2)

        if _discord_logged_in(page):
            ctx.close()
            return profile

        for sel in (
            'input[name="email"]',
            'input[type="email"]',
            'input[autocomplete="email"]',
        ):
            if page.locator(sel).count():
                page.locator(sel).first.fill(email)
                break
        for sel in (
            'input[name="password"]',
            'input[type="password"]',
        ):
            if page.locator(sel).count():
                page.locator(sel).first.fill(password)
                break

        for sel in ('button[type="submit"]', 'button:has-text("Log In")'):
            if page.locator(sel).count():
                page.locator(sel).first.click()
                break

        time.sleep(5)
        try:
            page.wait_for_url("**/channels/**", timeout=60_000)
        except Exception:
            pass
        time.sleep(2)

        if not _discord_logged_in(page):
            raise RuntimeError(
                "Discord login failed — check DISCORD_LOGIN_EMAIL/PASSWORD or complete 2FA on hub once"
            )
        ctx.close()
    finally:
        pw.stop()
    return profile


def _ensure_discord_logged_in(page) -> None:
    page.goto("https://discord.com/channels/@me", wait_until="domcontentloaded", timeout=120_000)
    time.sleep(2)
    if _discord_logged_in(page):
        return
    login_discord_session(headless=True)
    page.goto("https://discord.com/channels/@me", wait_until="domcontentloaded", timeout=120_000)
    time.sleep(2)
    if not _discord_logged_in(page):
        raise RuntimeError("Discord not logged in after login_discord_session")


def _guild_channel_urls() -> list[tuple[str, str]]:
    """Named channel URLs from env."""
    guild = (settings.discord_guild_id or "").strip()
    if not guild:
        return []
    out: list[tuple[str, str]] = []
    for cid in (settings.discord_channel_ids or "").replace(";", ",").split(","):
        cid = cid.strip()
        if cid:
            out.append((f"channel-{cid}", f"https://discord.com/channels/{guild}/{cid}"))
    if not out:
        out.append(("guild-home", f"https://discord.com/channels/{guild}"))
    return out


def _discover_guild_channels(page) -> list[tuple[str, str]]:
    """Best-effort: find Momentum / academy guild links from Discord sidebar."""
    found: list[tuple[str, str]] = []
    try:
        links = page.eval_on_selector_all(
            "a[href*='/channels/']",
            "els => els.map(e => ({href: e.href, text: (e.innerText||'').trim()}))",
        )
        for row in links or []:
            href = str(row.get("href") or "")
            text = str(row.get("text") or "")
            if "/channels/" not in href:
                continue
            parts = href.split("/channels/")[-1].strip("/").split("/")
            if len(parts) < 2:
                continue
            guild, channel = parts[0], parts[1]
            if guild.isdigit() and channel.isdigit():
                label = text or f"channel-{channel}"
                found.append((label[:60], href.split("?")[0]))
    except Exception:
        pass
    # Prefer channels whose label mentions momentum / academy / shop
    priority = ("momentum", "academy", "shop", "dojo", "weekly", "product")
    found.sort(
        key=lambda t: (
            0
            if any(p in t[0].lower() for p in priority)
            else 1,
            t[0].lower(),
        )
    )
    # Dedupe by URL
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for name, url in found:
        if url in seen:
            continue
        seen.add(url)
        out.append((name, url))
    return out[:12]


def crawl_discord(*, scroll_passes: int = 8, max_chars: int = 40_000) -> Path:
    """
    Read-only Discord web scrape. Requires prior login in profile discord/.
    Writes data/research/course/inbox/discord-crawl-YYYY-MM-DD.md
    """
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    profile = _discord_profile()
    profile.mkdir(parents=True, exist_ok=True)
    inbox = settings.data_dir / "research" / "course" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = inbox / f"discord-crawl-{stamp}.md"

    targets = _guild_channel_urls()
    discover_mode = not targets
    if discover_mode:
        targets = [("discord-home", "https://discord.com/channels/@me")]

    pw = sync_playwright().start()
    lines = [
        f"# Discord crawl — {stamp}",
        "",
        "**Read-only.** Never clicks Send. Profile: `data/browser_profile/discord/`",
        "",
    ]
    try:
        ctx = launch_stealth_context(pw, headless=True, profile_dir=profile)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        _ensure_discord_logged_in(page)

        if discover_mode:
            page.goto(targets[0][1], wait_until="domcontentloaded", timeout=120_000)
            time.sleep(4)
            discovered = _discover_guild_channels(page)
            if discovered:
                targets = discovered
                lines.append(f"Discovered {len(discovered)} channel links from sidebar.")
                lines.append("")

        for name, url in targets:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=120_000)
                time.sleep(3)
                for _ in range(scroll_passes):
                    page.keyboard.press("PageUp")
                    time.sleep(0.3)
                for _ in range(scroll_passes * 2):
                    page.keyboard.press("PageDown")
                    time.sleep(0.4)
                body = page.inner_text("body") or ""
                body = re.sub(r"\n{3,}", "\n\n", body).strip()[:max_chars]
                hint = "logged in" if "direct messages" in body.lower() or "#" in body else "check login"
                lines.extend([f"## {name}", "", f"URL: {page.url}", f"Session: {hint}", ""])
                lines.append(body or "(no text — log in once: browser.cli open discord --block)")
                lines.append("")
            except Exception as exc:
                lines.extend([f"## {name}", "", f"ERROR: {exc}", ""])
        ctx.close()
    finally:
        pw.stop()

    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return out_path
