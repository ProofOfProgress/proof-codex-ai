"""vidIQ keyword intelligence — browser session, MCP API key, or CSV export."""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from shorts_bot.config import settings

_MCP_URL = "https://mcp.vidiq.com/mcp"
_KEYWORD_URL = "https://app.vidiq.com/research/explore?tab=keywords"


@dataclass
class VidIQKeyword:
    keyword: str
    search_volume: str = ""
    competition: str = ""
    overall_score: str = ""


@dataclass
class VidIQResult:
    topic: str
    keywords: list[VidIQKeyword] = field(default_factory=list)
    source: str = ""
    message: str = ""

    def context_block(self, *, max_chars: int = 2000) -> str:
        if not self.keywords:
            return ""
        lines = [f"VIDIQ KEYWORD DATA ({self.source}):"]
        for kw in self.keywords[:15]:
            parts = [kw.keyword]
            if kw.overall_score:
                parts.append(f"score={kw.overall_score}")
            if kw.search_volume:
                parts.append(f"vol={kw.search_volume}")
            if kw.competition:
                parts.append(f"comp={kw.competition}")
            lines.append("- " + " | ".join(parts))
        if self.message:
            lines.append(f"Note: {self.message}")
        return "\n".join(lines)[:max_chars]


def _parse_keyword_rows(text: str) -> list[VidIQKeyword]:
    """Best-effort parse of vidIQ keyword table text."""
    out: list[VidIQKeyword] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or len(line) < 4:
            continue
        lower = line.lower()
        if lower in {"keyword", "search volume", "competition", "overall score"} or (
            "search volume" in lower and "competition" in lower and len(line) < 60
        ):
            continue
        # Tab or multi-space separated columns
        cols = re.split(r"\t+|\s{2,}", line)
        if len(cols) >= 2:
            kw = VidIQKeyword(
                keyword=cols[0][:80],
                search_volume=cols[1] if len(cols) > 1 else "",
                competition=cols[2] if len(cols) > 2 else "",
                overall_score=cols[3] if len(cols) > 3 else "",
            )
            if kw.keyword and not kw.keyword.startswith("#"):
                out.append(kw)
    return out


def _vidiq_mcp_keywords(topic: str) -> VidIQResult | None:
    """Call vidIQ MCP HTTP endpoint when VIDIQ_API_KEY is set (Max plan)."""
    key = (settings.vidiq_api_key or "").strip()
    if not key:
        return None

    prompt = (
        f"Find low-competition YouTube Shorts keywords related to: {topic}. "
        "Return top keywords with search volume and competition scores."
    )
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "keyword_research",
                "arguments": {"query": topic, "prompt": prompt},
            },
        }
    ).encode()
    req = urllib.request.Request(
        _MCP_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "User-Agent": "SoftContinuity/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except (OSError, urllib.error.HTTPError, json.JSONDecodeError):
        return None

    content = ""
    result = data.get("result") or {}
    if isinstance(result, dict):
        content = str(result.get("content") or result.get("text") or "")
    elif isinstance(result, str):
        content = result
    if not content:
        return None

    keywords = _parse_keyword_rows(content)
    if not keywords:
        keywords = [
            VidIQKeyword(keyword=line.strip("- ").strip()[:80])
            for line in content.splitlines()
            if line.strip() and len(line.strip()) > 3
        ][:12]
    return VidIQResult(topic=topic, keywords=keywords, source="vidiq_mcp_api", message="via MCP API key")


def _vidiq_browser_keywords(topic: str) -> VidIQResult:
    """Scrape vidIQ keyword research using saved browser profile."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(settings.browser_profile_dir),
            headless=True,
            viewport={"width": 1400, "height": 900},
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(_KEYWORD_URL, wait_until="domcontentloaded", timeout=120000)
        time.sleep(2)
        body = (page.inner_text("body") or "").lower()
        if "sign in" in body or "log in" in body or "create account" in body:
            context.close()
            return VidIQResult(
                topic=topic,
                source="vidiq_browser",
                message="Not logged in — run: python3 -m shorts_bot.login_handoff --only vidiq",
            )

        # Search input — vidIQ uses various selectors
        search = page.locator(
            'input[type="search"], input[placeholder*="keyword" i], input[placeholder*="search" i]'
        ).first
        try:
            search.wait_for(state="visible", timeout=15000)
            search.fill(topic)
            search.press("Enter")
            time.sleep(4)
        except Exception:
            context.close()
            return VidIQResult(
                topic=topic,
                source="vidiq_browser",
                message="Could not find keyword search box — UI may have changed.",
            )

        text = page.inner_text("main") or page.inner_text("body") or ""
        context.close()

    keywords = _parse_keyword_rows(text)
    if not keywords:
        # Fallback: lines after "related" / "matching"
        for line in text.splitlines():
            clean = line.strip()
            if 3 < len(clean) < 60 and clean[0].isalnum():
                keywords.append(VidIQKeyword(keyword=clean))
            if len(keywords) >= 10:
                break

    return VidIQResult(
        topic=topic,
        keywords=keywords[:15],
        source="vidiq_browser",
        message="" if keywords else "No keyword rows parsed — export CSV from vidIQ web app.",
    )


def import_vidiq_csv(path: Path) -> VidIQResult:
    topic = path.stem.replace("_", " ")
    keywords: list[VidIQKeyword] = []
    with path.open(encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kw = (
                row.get("Keyword")
                or row.get("keyword")
                or row.get("Term")
                or row.get("term")
                or ""
            ).strip()
            if not kw:
                continue
            keywords.append(
                VidIQKeyword(
                    keyword=kw,
                    search_volume=str(row.get("Search Volume") or row.get("search_volume") or ""),
                    competition=str(row.get("Competition") or row.get("competition") or ""),
                    overall_score=str(row.get("Overall Score") or row.get("score") or ""),
                )
            )
    return VidIQResult(topic=topic, keywords=keywords[:30], source="vidiq_csv", message=str(path))


def _latest_csv_export() -> Path | None:
    folder = settings.data_dir / "vidiq_exports"
    if not folder.exists():
        return None
    files = sorted(folder.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def vidiq_keyword_lookup(topic: str) -> VidIQResult | None:
    """Best available vidIQ path: MCP API → browser → recent CSV export."""
    if not settings.vidiq_enabled:
        return None

    mcp = _vidiq_mcp_keywords(topic)
    if mcp and mcp.keywords:
        return mcp

    browser: VidIQResult | None = None
    if settings.vidiq_use_browser:
        try:
            browser = _vidiq_browser_keywords(topic)
            if browser.keywords:
                return browser
        except Exception as exc:
            browser = VidIQResult(topic=topic, source="vidiq_browser", message=str(exc)[:200])

    csv_path = _latest_csv_export()
    if csv_path:
        imported = import_vidiq_csv(csv_path)
        if imported.keywords:
            imported.topic = topic
            imported.message = f"Using export {csv_path.name}"
            return imported

    return mcp or browser


def check_vidiq_session() -> tuple[bool, str]:
    """Quick login probe for login_status."""
    if (settings.vidiq_api_key or "").strip():
        return True, "VIDIQ_API_KEY set (MCP API)"
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(settings.browser_profile_dir),
                headless=True,
                viewport={"width": 1280, "height": 900},
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(_KEYWORD_URL, wait_until="domcontentloaded", timeout=90000)
            body = (page.inner_text("body") or "").lower()
            context.close()
        if "sign in" in body or "log in" in body:
            return False, "Not signed in"
        return True, "Browser session saved"
    except Exception as exc:
        return False, str(exc)[:120]
