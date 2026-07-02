"""Kalodata UI scout on hub — load owner filter URLs, capture product list."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from shorts_bot.config import settings
from shorts_bot.tiktok_shop import kalodata_filters
from shorts_bot.tiktok_shop.product_scout import ScoutProduct, _score_middle_core, _score_two_hundred


def _profile_dir() -> Path:
    base = settings.browser_profile_dir
    return base / "kalodata"


def _walk_product_dicts(node: Any, out: list[dict[str, Any]], *, depth: int = 0) -> None:
    if depth > 8:
        return
    if isinstance(node, dict):
        keys = {k.lower() for k in node}
        nameish = any(k in keys for k in ("productname", "product_name", "title", "name"))
        idish = any(k in keys for k in ("productid", "product_id", "id"))
        if nameish and (idish or "price" in keys or "revenue" in keys or "gmv" in keys):
            out.append(node)
        for val in node.values():
            _walk_product_dicts(val, out, depth=depth + 1)
    elif isinstance(node, list):
        for item in node:
            _walk_product_dicts(item, out, depth=depth + 1)


def extract_products_from_json(payload: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    _walk_product_dicts(payload, found)
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in found:
        pid = str(
            row.get("productId")
            or row.get("product_id")
            or row.get("id")
            or row.get("productName")
            or row.get("product_name")
            or row.get("title")
            or ""
        )
        if pid in seen:
            continue
        seen.add(pid)
        deduped.append(row)
    return deduped


def _num(raw: Any, default: float = 0.0) -> float:
    if raw is None:
        return default
    if isinstance(raw, (int, float)):
        return float(raw)
    text = str(raw).replace("$", "").replace(",", "").replace("%", "").strip()
    try:
        return float(text)
    except ValueError:
        return default


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    name = str(
        row.get("productName")
        or row.get("product_name")
        or row.get("title")
        or row.get("name")
        or ""
    ).strip()
    pid = str(row.get("productId") or row.get("product_id") or row.get("id") or "").strip()
    price = _num(
        row.get("price")
        or row.get("avgPrice")
        or row.get("unitPrice")
        or row.get("spu_avg_price")
    )
    rate_raw = _num(
        row.get("commissionRate")
        or row.get("commission_rate")
        or row.get("product_commission_rate")
    )
    rate = rate_raw / 100.0 if rate_raw > 1 else rate_raw
    gmv = _num(
        row.get("revenue")
        or row.get("gmv")
        or row.get("totalRevenue")
        or row.get("total_sale_gmv_amt")
        or row.get("total_sale_gmv_7d_amt")
    )
    creators = int(
        _num(row.get("creatorCount") or row.get("creators") or row.get("total_ifl_cnt"))
    )
    videos = int(_num(row.get("videoCount") or row.get("videos") or row.get("total_video_cnt")))
    cover = str(row.get("coverUrl") or row.get("cover_url") or row.get("image") or "").strip()
    return {
        "product_id": pid,
        "product_name": name,
        "spu_avg_price": price,
        "product_commission_rate": rate * 100 if rate <= 1 else rate,
        "total_sale_gmv_amt": gmv,
        "total_ifl_cnt": creators,
        "total_video_cnt": videos,
        "cover_url": cover,
    }


def _row_to_scout(row: dict[str, Any], *, preset: str) -> ScoutProduct | None:
    merged = _normalize_row(row)
    name = merged.get("product_name") or ""
    if not name:
        return None
    scorer = _score_two_hundred if preset == "two_hundred" else _score_middle_core
    score, _issues = scorer(merged)
    price = float(merged.get("spu_avg_price") or 0)
    rate = float(merged.get("product_commission_rate") or 0) / 100.0
    if rate > 1:
        rate /= 100.0
    return ScoutProduct(
        product_id=str(merged.get("product_id") or ""),
        product_name=name,
        price=price,
        commission_rate=rate,
        commission_usd=round(price * rate, 2),
        gmv_period=float(merged.get("total_sale_gmv_amt") or 0),
        creators=int(merged.get("total_ifl_cnt") or 0),
        videos=int(merged.get("total_video_cnt") or 0),
        preset=preset,
        score=score,
        cover_url=str(merged.get("cover_url") or ""),
        region=(kalodata_filters.load_config().get("region") or settings.kalodata_region or "US"),
    )


def _capture_from_page(page, *, wait_s: float = 6.0) -> list[dict[str, Any]]:
    captured: list[dict[str, Any]] = []

    def on_response(response) -> None:
        try:
            if response.request.resource_type not in ("xhr", "fetch"):
                return
            url = response.url.lower()
            if "product" not in url and "rank" not in url and "search" not in url:
                return
            body = response.json()
            captured.extend(extract_products_from_json(body))
        except Exception:
            return

    page.on("response", on_response)
    time.sleep(wait_s)
    if captured:
        return captured

    # DOM fallback: markdown-ish table text
    try:
        text = page.inner_text("body") or ""
    except Exception:
        text = ""
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        if "$" not in line or len(line) < 10:
            continue
        rows.append({"product_name": line[:120], "title": line[:120]})
    return rows


def scout_via_hub_ui(*, preset: str = "middle_core", limit: int = 10) -> list[ScoutProduct]:
    """
    Run on the hub (logged-in Kalodata session). Requires preset filter_url in kalodata_filters.json.
    """
    if not settings.browser_enabled:
        raise RuntimeError("Browser disabled — set BROWSER_ENABLED=true on hub")

    url = kalodata_filters.preset_filter_url(preset)
    if not url:
        block = kalodata_filters.preset_block(preset)
        ref = block.get("filters_reference") or {}
        raise RuntimeError(
            f"Kalodata hub scout needs filter_url for preset={preset!r}. "
            f"Owner: log into Kalodata on hub → apply filters ({ref}) → copy URL → "
            f"paste in {kalodata_filters.filters_path()}. "
            "See docs/FOR_OWNER_KALODATA_HUB_SETUP.md"
        )

    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    profile = _profile_dir()
    profile.mkdir(parents=True, exist_ok=True)
    pw = sync_playwright().start()
    captured_rows: list[dict[str, Any]] = []
    try:
        context = launch_stealth_context(pw, headless=True, profile_dir=profile)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=120000)
        captured_rows = _capture_from_page(page, wait_s=8.0)
        body = (page.inner_text("body") or "").lower()
        if "log in" in body or "sign in" in body:
            raise RuntimeError(
                "Kalodata session expired on hub. Owner: run once on hub:\n"
                "  python3 -m shorts_bot.browser.cli open kalodata --minutes 10\n"
                "Log in, then retry scout."
            )
        context.close()
    finally:
        pw.stop()

    if not captured_rows:
        raise RuntimeError(
            f"Kalodata page loaded but no products captured for {preset!r}. "
            "Check filter_url is still valid or increase wait time."
        )

    scored: list[ScoutProduct] = []
    for row in captured_rows:
        item = _row_to_scout(row, preset=preset)
        if item and item.score >= 40:
            scored.append(item)
    scored.sort(key=lambda p: p.score, reverse=True)
    if not scored:
        # Keep top rows even if scorer strict — owner filters already applied
        for row in captured_rows[:limit]:
            item = _row_to_scout(row, preset=preset)
            if item:
                scored.append(item)
    return scored[:limit]
