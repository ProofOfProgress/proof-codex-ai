"""InVideo Agent One — conversational filmmaker via browser session."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from shorts_bot.config import settings

WORKSPACES_URL = "https://ai.invideo.io/workspaces"
AGENT_MODE_LABELS = ("Agent mode", "Agent One", "Agent")
PROMPT_SELECTORS = (
    "#v40-agent-prompt-input",
    ".v40-agent-prompt-input",
    "textarea[placeholder*='Plan a script']",
    "textarea",
)
SUBMIT_SELECTORS = (
    "#v40-agent-prompt-submit",
    ".v40-agent-prompt-submit",
    "button[type='submit']",
)


@dataclass
class AgentOneResult:
    ok: bool
    message: str
    project_url: str = ""
    workspace_url: str = ""
    response_excerpt: str = ""


def _state_path() -> Path:
    return settings.data_dir / "invideo_agent_one.json"


def load_agent_state() -> dict[str, Any]:
    path = _state_path()
    if not path.exists():
        return {}
    try:
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_agent_state(data: dict[str, Any]) -> None:
    import json

    path = _state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def copilot_url() -> str:
    saved = (load_agent_state().get("copilot_url") or "").strip()
    if saved:
        return saved
    custom = (getattr(settings, "invideo_copilot_url", None) or "").strip()
    return custom or WORKSPACES_URL


def _is_logged_in_url(url: str) -> bool:
    u = url.lower()
    return "/workspace" in u or "/workspaces" in u


def _open_agent_mode(page) -> str:
    """Return copilot URL after entering Agent mode."""
    page.goto(WORKSPACES_URL, wait_until="domcontentloaded", timeout=120_000)
    time.sleep(3)
    if not _is_logged_in_url(page.url):
        raise RuntimeError("Not logged into InVideo — run: python3 -m shorts_bot.invideo.handoff_cli")

    for label in AGENT_MODE_LABELS:
        loc = page.get_by_text(label, exact=False)
        if loc.count():
            loc.first.click(timeout=10_000)
            time.sleep(4)
            break

    if "v40-copilot" not in page.url and "copilot" not in page.url:
        raise RuntimeError(f"Could not open Agent One — landed on {page.url}")

    if page.get_by_text("New project", exact=False).count():
        page.get_by_text("New project", exact=False).first.click(timeout=10_000)
        time.sleep(4)

    save_agent_state({"copilot_url": page.url, "updated_at": time.time()})
    return page.url


def _find_prompt(page):
    for sel in PROMPT_SELECTORS:
        loc = page.locator(sel)
        if loc.count():
            return loc.first
    raise RuntimeError("Agent One prompt input not found — UI may have changed")


def _find_submit(page):
    for sel in SUBMIT_SELECTORS:
        loc = page.locator(sel)
        if loc.count():
            return loc.first
    raise RuntimeError("Agent One send button not found")


def send_prompt(
    prompt: str,
    *,
    open_browser: bool = False,
    wait_sec: int = 30,
    headless: bool | None = None,
) -> AgentOneResult:
    """
    Send a message to InVideo Agent One (chat panel).
    Requires saved browser login at ai.invideo.io/workspaces.
    """
    from shorts_bot.invideo.system_context import wrap_invideo_prompt

    prompt = wrap_invideo_prompt(prompt)
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    use_headless = settings.browser_headless if headless is None else headless
    if open_browser:
        use_headless = False

    excerpt = ""
    project_url = ""
    workspace_url = ""

    with sync_playwright() as p:
        ctx = launch_stealth_context(p, headless=use_headless)
        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            start_url = copilot_url()
            if start_url == WORKSPACES_URL or "v40-copilot" not in start_url:
                workspace_url = _open_agent_mode(page)
            else:
                page.goto(start_url, wait_until="domcontentloaded", timeout=120_000)
                time.sleep(4)
                workspace_url = page.url
                if page.get_by_text("New project", exact=False).count():
                    page.get_by_text("New project", exact=False).first.click(timeout=10_000)
                    time.sleep(3)

            inp = _find_prompt(page)
            inp.click()
            inp.fill(prompt.strip())
            time.sleep(0.5)
            _find_submit(page).click()

            deadline = time.time() + wait_sec
            while time.time() < deadline:
                time.sleep(3)
                body = page.inner_text("body") or ""
                if len(body) > 500 and prompt[:30] not in body[-800:]:
                    excerpt = body[-1200:]
                    break

            project_url = page.url
            save_agent_state(
                {
                    "copilot_url": project_url,
                    "last_prompt": prompt[:500],
                    "updated_at": time.time(),
                }
            )

            if open_browser and not use_headless:
                time.sleep(max(60, wait_sec))

        finally:
            ctx.close()

    ok = bool(excerpt or project_url)
    return AgentOneResult(
        ok=ok,
        message="Sent to Agent One — check Desktop for reply and Generate button"
        if ok
        else "Message sent but no response captured yet — open browser to continue",
        project_url=project_url,
        workspace_url=workspace_url,
        response_excerpt=excerpt[:800],
    )


def probe_agent_one_session() -> tuple[bool, str]:
    """Quick headless check — can we reach Agent One workspace?"""
    try:
        from playwright.sync_api import sync_playwright

        from shorts_bot.browser.stealth import launch_stealth_context

        with sync_playwright() as p:
            ctx = launch_stealth_context(p, headless=True)
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(WORKSPACES_URL, wait_until="domcontentloaded", timeout=90_000)
            time.sleep(3)
            url = page.url
            body = (page.inner_text("body") or "").lower()
            ctx.close()
        if _is_logged_in_url(url) and "agent mode" in body:
            return True, "Logged in — Agent mode available"
        if "log in" in body or "signup" in url:
            return False, "Not logged in — run handoff_cli"
        return False, f"Session unclear ({url})"
    except Exception as exc:
        return False, str(exc)[:120]
