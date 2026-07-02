"""Live Kalodata table scrape via hub desktop screenshot — when Edge shows filtered list."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

from shorts_bot.agent_credentials import load_agent_credentials
from shorts_bot.config import settings
from shorts_bot.tiktok_shop.product_scout import ScoutProduct


def _gemini_key() -> str:
    load_agent_credentials()
    import os

    return (os.environ.get("GEMINI_API_KEY") or settings.gemini_api_key or "").strip()


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def hub_screenshot(rel_path: str = "data/desktop_hub/kalodata_scrape.png") -> Path:
    # Scroll product table so revenue column is visible before capture.
    try:
        client = __import__(
            "shorts_bot.desktop_hub.client", fromlist=["DesktopHubClient"]
        ).DesktopHubClient()
        client.ping()
        for _ in range(3):
            client.press("pagedown")
            time.sleep(0.4)
    except Exception:
        pass
    subprocess.run(
        [sys.executable, "-m", "shorts_bot.desktop_hub.cli", "screenshot", "--out", rel_path],
        cwd=_root(),
        check=True,
    )
    return settings.data_dir / "desktop_hub" / Path(rel_path).name


def gemini_extract_products(image: Path, *, limit: int = 20) -> list[dict]:
    from google import genai

    from shorts_bot.llm.gemini_utils import call_with_retry, cheap_model

    key = _gemini_key()
    if not key:
        return []
    client = genai.Client(api_key=key)
    model = cheap_model()
    prompt = (
        f"Extract up to {limit} TikTok Shop products from this Kalodata product LIST table screenshot. "
        "Read the TABLE columns carefully — do not guess. "
        "revenue must be the Revenue / GMV column (often thousands or millions, e.g. 15000 or 1.2M). "
        "If revenue cell shows K/M suffix, convert to full USD number. "
        "commission_pct is the Commission % column (reject rows if not visible). "
        "Return ONLY JSON array. Each object: "
        "product_name, avg_unit_price, commission_pct, revenue, growth_pct, creators, videos. "
        "Numbers only in JSON."
    )
    def _extract_once() -> list[dict]:
        resp = client.models.generate_content(
            model=model,
            contents=[prompt, genai.types.Part.from_bytes(data=image.read_bytes(), mime_type="image/png")],
        )
        raw = (resp.text or "").strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
        data = json.loads(raw)
        return data if isinstance(data, list) else []

    try:
        return call_with_retry(_extract_once, label=f"kalodata-scrape:{model}")
    except Exception as exc:
        print(f"WARN gemini extract failed: {exc}", flush=True)
        return []


def _parse_revenue(raw: object) -> float:
    if raw is None:
        return 0.0
    text = str(raw).replace("$", "").replace(",", "").strip().upper()
    mult = 1.0
    if text.endswith("K"):
        mult = 1_000.0
        text = text[:-1]
    elif text.endswith("M"):
        mult = 1_000_000.0
        text = text[:-1]
    try:
        return float(text) * mult
    except ValueError:
        return 0.0


def rows_to_scout(rows: list[dict], *, preset: str = "kalodata_live") -> list[ScoutProduct]:
    out: list[ScoutProduct] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = str(row.get("product_name") or row.get("name") or "").strip()
        if not name:
            continue
        price = float(row.get("avg_unit_price") or row.get("price") or 0)
        comm = float(row.get("commission_pct") or row.get("commission") or 0)
        if comm > 1:
            comm /= 100.0
        if comm <= 0:
            continue
        creators = int(float(row.get("creators") or 0))
        gmv = _parse_revenue(row.get("revenue") or row.get("gmv"))
        videos = int(float(row.get("videos") or 0))
        out.append(
            ScoutProduct(
                product_id="",
                product_name=name,
                price=price,
                commission_rate=comm,
                commission_usd=round(price * comm, 2),
                gmv_period=gmv,
                creators=creators,
                videos=videos,
                preset=preset,
                score=50.0,
            )
        )
    return out


def scout_live_edge_table(*, limit: int = 15, preset: str = "kalodata_live") -> list[ScoutProduct]:
    """Screenshot owner's screen (Kalodata list visible) → Gemini parse → quality gate."""
    if not _gemini_key():
        return []
    shot = hub_screenshot()
    rows = gemini_extract_products(shot, limit=limit)
    if not rows:
        return []
    from shorts_bot.tiktok_shop.scout_product_quality import filter_quality_products

    raw = rows_to_scout(rows, preset=preset)
    passed, rejected = filter_quality_products(raw, limit=limit, strict=True)
    for p, q in rejected[:3]:
        print(f"LIVE REJECT {p.product_name[:40]}: {'; '.join(q.issues)}", flush=True)
    return passed
