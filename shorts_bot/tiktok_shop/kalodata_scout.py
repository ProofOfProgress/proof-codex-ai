"""Scout products via Kalodata KaloPilot (coach filters → products.json)."""

from __future__ import annotations

import json
import re
from typing import Any

from shorts_bot.config import settings
from shorts_bot.tiktok_shop import kalodata_client
from shorts_bot.tiktok_shop.product_scout import ScoutProduct


def _scout_query(*, preset: str, limit: int) -> str:
    """Natural-language query with coach-call filters (GROUP_CALLS 2026-06-30)."""
    region = (settings.kalodata_region or "US").strip()
    base = (
        f"{region} TikTok Shop affiliate product research. "
        f"Find up to {limit} products matching ALL filters where possible:\n"
        "- Last 7 days revenue over $10,000\n"
        "- Revenue mainly from video (not live-only)\n"
        "- Revenue growth at least 30%\n"
        "- Average unit price over $80 (high ticket)\n"
        "- Creator count at most 200\n"
        "- Affiliate commission at least 8%\n"
        "- Prefer rising / pre-breakout (accelerating GMV, not peaked)\n"
        "- Top videos should show brand ad spend when available\n"
    )
    if preset == "two_hundred":
        base += "- Emphasize yesterday's hot movers (200 method style)\n"
    else:
        base += "- Emphasize middle-core steady winners with room to grow\n"
    base += (
        "\nReturn a markdown table with columns exactly:\n"
        "product_name | product_id | price_usd | commission_pct | gmv_usd | creators | videos | trend | cover_url\n"
        "Use real Kalodata data only. product_id = TikTok Shop numeric ID if known."
    )
    return base


def _parse_table_rows(text: str) -> list[dict[str, Any]]:
    """Best-effort parse of markdown table from KaloPilot response."""
    lines = [ln.strip() for ln in text.splitlines() if "|" in ln]
    if len(lines) < 2:
        return []
    header = [c.strip().lower().replace(" ", "_") for c in lines[0].strip("|").split("|")]
    rows: list[dict[str, Any]] = []
    for ln in lines[2:]:  # skip header + separator
        if re.match(r"^[\|\s\-:]+$", ln):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def _row_to_scout(row: dict[str, Any], *, preset: str) -> ScoutProduct | None:
    name = str(row.get("product_name") or row.get("name") or "").strip()
    pid = str(row.get("product_id") or row.get("id") or "").strip()
    if not name:
        return None

    def _float(key: str, default: float = 0.0) -> float:
        raw = str(row.get(key) or "").replace("$", "").replace(",", "").replace("%", "").strip()
        try:
            return float(raw)
        except ValueError:
            return default

    price = _float("price_usd") or _float("price")
    comm_pct = _float("commission_pct") or _float("commission_rate")
    rate = comm_pct / 100.0 if comm_pct > 1 else comm_pct
    gmv = _float("gmv_usd") or _float("gmv")
    creators = int(_float("creators"))
    videos = int(_float("videos"))
    commission_usd = round(price * rate, 2) if price and rate else 0.0
    score = 50.0
    if gmv >= 10_000:
        score += 20
    if creators and creators <= 200:
        score += 15
    if rate >= 0.08:
        score += 15
    if price >= 80:
        score += 10

    return ScoutProduct(
        product_id=pid,
        product_name=name,
        price=price,
        commission_rate=rate,
        commission_usd=commission_usd,
        gmv_period=gmv,
        creators=creators,
        videos=videos,
        preset=preset,
        score=score,
        cover_url=str(row.get("cover_url") or "").strip(),
        region=(settings.kalodata_region or "US").strip(),
    )


def _extract_with_gemini(text: str, report: str | None, *, limit: int) -> list[dict[str, Any]]:
    key = (settings.gemini_api_key or "").strip()
    if not key:
        return []
    try:
        from google import genai
    except ImportError:
        return []

    combined = f"{text}\n\n{report or ''}".strip()
    if not combined:
        return []

    client = genai.Client(api_key=key)
    model = (settings.gemini_model or "gemini-2.5-flash-lite").strip()
    prompt = (
        f"Extract up to {limit} TikTok Shop products from this Kalodata research response. "
        "Return ONLY a JSON array of objects with keys: "
        "product_name, product_id, price_usd, commission_pct, gmv_usd, creators, videos, cover_url. "
        "Use numbers not strings for numeric fields. Empty array if none found.\n\n"
        f"{combined[:80000]}"
    )
    resp = client.models.generate_content(model=model, contents=[prompt])
    raw = (resp.text or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def scout_via_kalodata(*, preset: str = "middle_core", limit: int = 10) -> list[ScoutProduct]:
    if not kalodata_client.configured():
        raise RuntimeError("Kalodata not configured — set KALODATA_PILOT_TOKEN")

    query = _scout_query(preset=preset, limit=limit)
    data = kalodata_client.query_and_wait(query)
    text = str(data.get("text") or "")
    report = str(data.get("report") or "") if data.get("report") else None
    combined = f"{text}\n{report or ''}"

    rows = _parse_table_rows(combined)
    if not rows:
        rows = _extract_with_gemini(text, report, limit=limit)

    products: list[ScoutProduct] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        item = _row_to_scout(row, preset=preset)
        if item:
            products.append(item)
        if len(products) >= limit:
            break

    if not products:
        raise RuntimeError(
            "Kalodata returned data but scout could not parse products. "
            "Check KaloPilot credits/membership or retry. "
            f"Preview: {combined[:400]!r}"
        )
    products.sort(key=lambda p: p.score, reverse=True)
    return products[:limit]
