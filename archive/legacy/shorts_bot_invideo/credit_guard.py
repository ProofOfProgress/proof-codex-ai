"""Parse InVideo Generate button credit cost — abort if over budget."""

from __future__ import annotations

import re

DEFAULT_MAX_CREDITS = 10


def parse_credit_cost(text: str) -> int | None:
    """Extract credit number from button/page text like 'Generate · 4 credits'."""
    if not text:
        return None
    patterns = (
        r"generate[^\d]{0,40}(\d{1,3})\s*credits?",
        r"(\d{1,3})\s*credits?\s*·?\s*generate",
        r"(\d{1,3})\s*credits?",
    )
    lower = text.lower()
    for pat in patterns:
        m = re.search(pat, lower, re.I)
        if m:
            return int(m.group(1))
    return None


def assert_credit_budget(text: str, *, max_credits: int = DEFAULT_MAX_CREDITS) -> int:
    """
    Return parsed credit cost. Raise if over max or unknown (safe default: refuse).
    """
    cost = parse_credit_cost(text)
    if cost is None:
        raise RuntimeError(
            "Could not read credit cost on Generate button — refusing to click. "
            "Open InVideo manually and confirm Basic tier shows ≤10 credits."
        )
    if cost > max_credits:
        raise RuntimeError(
            f"InVideo wants {cost} credits — max allowed is {max_credits}. "
            "Switch to Basic + stock-only (no twin, no Pro) and retry."
        )
    return cost


def quote_generate_credits(
    project_url: str,
    *,
    max_wait_sec: int = 120,
    select_basic: bool = True,
) -> int:
    """Open InVideo project, select Basic/Shorts if visible, return Generate credit cost (no click)."""
    import time

    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    with sync_playwright() as p:
        ctx = launch_stealth_context(p, headless=True)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(project_url, wait_until="networkidle", timeout=120_000)
        time.sleep(3)

        body = page.inner_text("body") or ""
        if "welcome to invideo ai" in body.lower() and "create new" not in body.lower():
            ctx.close()
            raise RuntimeError("Not logged into InVideo — run handoff_cli")

        deadline = time.time() + max_wait_sec
        while time.time() < deadline:
            body = page.inner_text("body") or ""
            gen = page.locator("button").filter(has_text="Generate")
            if gen.count() or page.get_by_text("Download", exact=True).count():
                break
            time.sleep(5)
        else:
            ctx.close()
            raise RuntimeError(f"No Generate button after {max_wait_sec}s")

        yt = page.get_by_text("YouTube Shorts", exact=False)
        if yt.count():
            yt.first.click(force=True)
            time.sleep(1)

        if select_basic:
            for label in ("Basic", "Licensed stock", "Stock"):
                loc = page.get_by_text(label, exact=False)
                if loc.count():
                    try:
                        loc.first.click(force=True, timeout=3000)
                        time.sleep(1)
                        break
                    except Exception:
                        pass

        body = page.inner_text("body") or ""
        gen = page.locator("button").filter(has_text="Generate")
        if not gen.count():
            if page.get_by_text("Download", exact=True).count():
                ctx.close()
                return 0
            ctx.close()
            raise RuntimeError("Generate button missing on project page")

        btn_text = gen.first.inner_text(timeout=5000)
        cost = parse_credit_cost(f"{btn_text}\n{body}")
        ctx.close()
        if cost is None:
            raise RuntimeError(
                f"Could not parse credit cost from button: {btn_text!r}"
            )
        return cost
