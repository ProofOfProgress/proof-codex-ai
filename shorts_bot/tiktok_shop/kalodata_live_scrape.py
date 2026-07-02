"""Live Kalodata table scrape via hub desktop screenshot — when Edge shows filtered list."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.product_scout import ScoutProduct


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def hub_screenshot(rel_path: str = "data/desktop_hub/kalodata_scrape.png") -> Path:
    subprocess.run(
        [sys.executable, "-m", "shorts_bot.desktop_hub.cli", "screenshot", "--out", rel_path],
        cwd=_root(),
        check=True,
    )
    return settings.data_dir / "desktop_hub" / Path(rel_path).name


def gemini_extract_products(image: Path, *, limit: int = 20) -> list[dict]:
    from google import genai

    key = (settings.gemini_api_key or "").strip()
    if not key:
        return []
    client = genai.Client(api_key=key)
    model = (settings.gemini_model or "gemini-2.5-flash-lite").strip()
    prompt = (
        f"Extract up to {limit} TikTok Shop products from this Kalodata product LIST table screenshot. "
        "Return ONLY JSON array. Each object must include: "
        "product_name, price, avg_unit_price, commission_pct, revenue, growth_pct, creators, videos. "
        "commission_pct is affiliate commission percent (number, e.g. 12 for 12%). "
        "revenue is period GMV in USD. Numbers only — no $ signs in JSON."
    )
    for attempt in range(4):
        try:
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
        except Exception as exc:
            if "503" not in str(exc) or attempt == 3:
                return []
            time.sleep(5 * (attempt + 1))
    return []


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
            comm = 0.10
        creators = int(float(row.get("creators") or 0))
        gmv = float(row.get("revenue") or row.get("gmv") or 0)
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
    if not settings.has_gemini:
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
