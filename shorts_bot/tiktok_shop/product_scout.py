"""Score TikTok Shop products using course filters (FastMoss when API wired)."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop import echotik_client
from shorts_bot.tiktok_shop.kalodata_rules import PRESET_200_METHOD, PRESET_MIDDLE_CORE
from shorts_bot.tiktok_shop.product_images import parse_cover_url


@dataclass
class ScoutProduct:
    product_id: str
    product_name: str
    price: float
    commission_rate: float
    commission_usd: float
    gmv_period: float
    creators: int
    videos: int
    preset: str
    score: float
    cover_url: str = ""
    region: str = "US"

    def to_dict(self) -> dict:
        return asdict(self)


def _commission_rate(raw: object) -> float:
    val = float(raw or 0)
    if val > 1:
        return val / 100.0
    return val


def _row_metrics(row: dict) -> tuple[float, float, float, int, int]:
    price = float(row.get("spu_avg_price") or row.get("min_price") or 0)
    rate = _commission_rate(row.get("product_commission_rate"))
    commission_usd = price * rate
    gmv = float(row.get("total_sale_gmv_amt") or row.get("total_sale_gmv_1d_amt") or 0)
    creators = int(row.get("total_ifl_cnt") or 0)
    videos = int(row.get("total_video_cnt") or 0)
    return price, rate, commission_usd, creators, videos


def _score_middle_core(row: dict) -> tuple[float, list[str]]:
    price, rate, commission_usd, creators, videos = _row_metrics(row)
    issues: list[str] = []
    score = 0.0
    gmv = float(row.get("total_sale_gmv_amt") or row.get("total_sale_gmv_7d_amt") or 0)

    if creators > PRESET_MIDDLE_CORE.creator_max:
        issues.append(f"too many creators ({creators})")
    else:
        score += 25
    if rate >= 0.20 or commission_usd >= 5:
        score += 25
    else:
        issues.append(f"low commission (${commission_usd:.2f}/sale)")
    if gmv >= 10_000:
        score += 25
    elif gmv >= 3_000:
        score += 12
    else:
        issues.append(f"low GMV (${gmv:.0f})")
    if videos >= 1:
        score += 15
    else:
        issues.append("no affiliate videos")
    if price >= 20:
        score += 10
    return score, issues


def _score_two_hundred(row: dict) -> tuple[float, list[str]]:
    price, rate, commission_usd, creators, videos = _row_metrics(row)
    issues: list[str] = []
    score = 0.0
    gmv = float(row.get("total_sale_gmv_amt") or row.get("total_sale_gmv_1d_amt") or 0)

    if creators > PRESET_200_METHOD.creator_max:
        issues.append(f"too many creators ({creators})")
    else:
        score += 30
    if gmv >= 10_000:
        score += 30
    elif gmv >= 5_000:
        score += 15
    else:
        issues.append(f"low yesterday GMV (${gmv:.0f})")
    if commission_usd >= 2:
        score += 20
    else:
        issues.append(f"tiny commission (${commission_usd:.2f})")
    if videos >= 1:
        score += 20
    return score, issues


def _yesterday_str() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


def _week_start_str() -> str:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return monday.isoformat()


def _fetch_rank_pages(*, rank_date: str, rank_type: int, pages: int) -> list[dict]:
    rows: list[dict] = []
    for page in range(1, pages + 1):
        batch = echotik_client.product_ranklist(
            date=rank_date,
            rank_type=rank_type,
            product_rank_field=1,
            page_num=page,
            page_size=10,
        )
        if not batch:
            break
        rows.extend(batch)
    return rows


def _fetch_daily_rank_rows(*, pages: int, start_days_back: int = 1, max_days_back: int = 7) -> list[dict]:
    """Walk back daily ranklists — T+1 lag often leaves yesterday empty."""
    for days_back in range(start_days_back, max_days_back + 1):
        rank_date = (date.today() - timedelta(days=days_back)).isoformat()
        rows = _fetch_rank_pages(rank_date=rank_date, rank_type=1, pages=pages)
        if rows:
            return rows
    return []


def fetch_rank_rows(*, preset: str, pages: int = 3) -> list[dict]:
    if not echotik_client.configured():
        raise RuntimeError("EchoTik not configured — see docs/FOR_OWNER_ECHOTIK_SETUP.md")

    if preset == "two_hundred":
        return _fetch_daily_rank_rows(pages=pages, start_days_back=1)

    # middle_core: weekly movers first, then latest daily ranklist with data
    rows = _fetch_rank_pages(rank_date=_week_start_str(), rank_type=2, pages=pages)
    if rows:
        return rows
    return _fetch_daily_rank_rows(pages=pages, start_days_back=1)


def scout_products(*, preset: str = "middle_core", limit: int = 10) -> list[ScoutProduct]:
    from shorts_bot.tiktok_shop import fastmoss_client

    if fastmoss_client.configured():
        ping = fastmoss_client.ping()
        raise RuntimeError(ping.get("message") or "FastMoss scout not wired yet — docs/FOR_OWNER_FASTMOSS_SETUP.md")

    raise RuntimeError(
        "Product scout uses **FastMoss only** (EchoTik retired). "
        "Subscribe at fastmoss.com — pick 8–10 products in the app (Launch path A) "
        "or add FASTMOSS_CLIENT_ID + FASTMOSS_CLIENT_SECRET when API scout ships. "
        "See docs/FOR_OWNER_FASTMOSS_SETUP.md"
    )

    # Legacy EchoTik path — unreachable until FastMoss scout replaces block above
    scorer = _score_two_hundred if preset == "two_hundred" else _score_middle_core
    raw_rows = fetch_rank_rows(preset=preset, pages=5)

    # Enrich top candidates with detail (cover URL)
    ids = [str(r.get("product_id") or "") for r in raw_rows[:30] if r.get("product_id")]
    details: dict[str, dict] = {}
    for i in range(0, len(ids), 10):
        chunk = ids[i : i + 10]
        for row in echotik_client.product_detail(chunk):
            pid = str(row.get("product_id") or "")
            if pid:
                details[pid] = row

    scored: list[tuple[float, dict, list[str]]] = []
    for row in raw_rows:
        pid = str(row.get("product_id") or "")
        merged = {**row, **details.get(pid, {})}
        score, issues = scorer(merged)
        if score >= 50 and not issues:
            scored.append((score, merged, issues))
        elif score >= 65:
            scored.append((score, merged, issues))

    scored.sort(key=lambda x: x[0], reverse=True)
    out: list[ScoutProduct] = []
    for score, row, _issues in scored[:limit]:
        price, rate, commission_usd, creators, videos = _row_metrics(row)
        out.append(
            ScoutProduct(
                product_id=str(row.get("product_id") or ""),
                product_name=str(row.get("product_name") or "").strip(),
                price=price,
                commission_rate=rate,
                commission_usd=round(commission_usd, 2),
                gmv_period=float(row.get("total_sale_gmv_amt") or 0),
                creators=creators,
                videos=videos,
                preset=preset,
                score=score,
                cover_url=parse_cover_url(row.get("cover_url")),
                region=str(row.get("region") or settings.echotik_region or "US"),
            )
        )

    # EchoTik detail batches can omit cover_url — re-fetch for final picks only.
    if out:
        final_ids = [p.product_id for p in out if p.product_id]
        final_details: dict[str, dict] = {}
        for i in range(0, len(final_ids), 10):
            for detail_row in echotik_client.product_detail(final_ids[i : i + 10]):
                pid = str(detail_row.get("product_id") or "")
                if pid:
                    final_details[pid] = detail_row
        for product in out:
            url = parse_cover_url(final_details.get(product.product_id, {}).get("cover_url"))
            if url:
                product.cover_url = url

    return out


def enrich_cover_urls(products: list[dict]) -> list[dict]:
    """Backfill cover_url from EchoTik product/detail for rows missing it."""
    missing = [
        str(p.get("product_id") or "")
        for p in products
        if p.get("product_id") and not parse_cover_url(p.get("cover_url"))
    ]
    if not missing or not echotik_client.configured():
        return products

    details: dict[str, dict] = {}
    for i in range(0, len(missing), 10):
        chunk = missing[i : i + 10]
        for row in echotik_client.product_detail(chunk):
            pid = str(row.get("product_id") or "")
            if pid:
                details[pid] = row

    out: list[dict] = []
    for row in products:
        pid = str(row.get("product_id") or "")
        merged = {**row, **details.get(pid, {})}
        url = parse_cover_url(merged.get("cover_url"))
        if url:
            merged["cover_url"] = url
        out.append(merged)
    return out


def products_path() -> Path:
    return settings.data_dir / "tiktok_shop" / "products.json"


def save_products(products: list[ScoutProduct]) -> Path:
    path = products_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([p.to_dict() for p in products], indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def save_product_dicts(products: list[dict]) -> Path:
    path = products_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(products, indent=2) + "\n", encoding="utf-8")
    return path


def load_products() -> list[dict]:
    path = products_path()
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []
