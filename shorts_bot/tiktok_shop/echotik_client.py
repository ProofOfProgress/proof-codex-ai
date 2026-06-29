"""EchoTik API client — TikTok Shop product research."""

from __future__ import annotations

import base64
from datetime import date, timedelta
from typing import Any

import httpx

from shorts_bot.config import settings

API_PREFIX = "/api/v3/echotik"


def configured() -> bool:
    user = (settings.echotik_username or "").strip()
    password = (settings.echotik_password or "").strip()
    if not user or not password:
        return False
    lower = (user + password).lower()
    return "placeholder" not in lower and "your-" not in lower


def _auth_header() -> dict[str, str]:
    user = (settings.echotik_username or "").strip()
    password = (settings.echotik_password or "").strip()
    if not user or not password:
        raise RuntimeError("EchoTik not configured — set ECHOTIK_USERNAME + ECHOTIK_PASSWORD")
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def _get(path: str, *, params: dict[str, Any]) -> dict[str, Any]:
    base = (settings.echotik_api_base or "https://open.echotik.live").rstrip("/")
    url = f"{base}{path}"
    with httpx.Client(timeout=60.0) as client:
        resp = client.get(url, params=params, headers=_auth_header())
    try:
        body = resp.json()
    except Exception as exc:
        raise RuntimeError(f"EchoTik non-JSON ({resp.status_code}): {resp.text[:200]}") from exc
    if resp.status_code >= 400 or body.get("code") not in (0, None):
        msg = body.get("message") or body
        raise RuntimeError(f"EchoTik error: {msg}")
    return body


def _list_data(path: str, *, params: dict[str, Any]) -> list[dict[str, Any]]:
    body = _get(path, params=params)
    data = body.get("data")
    return data if isinstance(data, list) else []


def ping(*, max_days_back: int = 7) -> dict[str, Any]:
    """
    One lightweight API call to verify credentials + quota.
    Walks back daily ranklists until data is found or max_days_back exhausted.
    """
    region = (settings.echotik_region or "US").strip()
    for days_back in range(1, max_days_back + 1):
        rank_date = (date.today() - timedelta(days=days_back)).isoformat()
        try:
            rows = product_ranklist(
                date=rank_date,
                region=region,
                rank_type=1,
                page_num=1,
                page_size=1,
            )
        except RuntimeError as exc:
            msg = str(exc)
            if "Usage Limit" in msg or "Quota" in msg:
                return {
                    "ok": False,
                    "error": "quota_exceeded",
                    "message": msg,
                    "region": region,
                }
            raise
        if rows:
            sample = rows[0]
            return {
                "ok": True,
                "region": region,
                "rank_date": rank_date,
                "sample_product": str(sample.get("product_name") or "")[:80],
                "sample_gmv": sample.get("total_sale_gmv_amt"),
            }
    return {
        "ok": True,
        "region": region,
        "rank_date": None,
        "message": f"No daily ranklist rows in last {max_days_back} days (T+1 lag is normal)",
    }


def product_ranklist(
    *,
    date: str,
    region: str | None = None,
    rank_type: int = 1,
    product_rank_field: int = 1,
    page_num: int = 1,
    page_size: int = 10,
) -> list[dict[str, Any]]:
    """
    Daily/weekly/monthly product rank list.
    rank_type: 1=day 2=week 3=month
    product_rank_field: 1=hot sales 2=hot promoted
    """
    return _list_data(
        f"{API_PREFIX}/product/ranklist",
        params={
            "date": date,
            "region": (region or settings.echotik_region or "US").strip(),
            "rank_type": rank_type,
            "product_rank_field": product_rank_field,
            "page_num": page_num,
            "page_size": min(10, max(1, page_size)),
        },
    )


def product_list(
    *,
    region: str | None = None,
    page_num: int = 1,
    page_size: int = 10,
    **filters: Any,
) -> list[dict[str, Any]]:
    """Filtered product list (T+1 warehouse). Pass filter kwargs matching API docs."""
    params: dict[str, Any] = {
        "region": (region or settings.echotik_region or "US").strip(),
        "page_num": page_num,
        "page_size": min(10, max(1, page_size)),
    }
    for key, val in filters.items():
        if val is not None:
            params[key] = val
    return _list_data(f"{API_PREFIX}/product/list", params=params)


def product_detail(product_ids: list[str]) -> list[dict[str, Any]]:
    ids = ",".join(i.strip() for i in product_ids if i.strip())[:500]
    if not ids:
        return []
    return _list_data(f"{API_PREFIX}/product/detail", params={"product_ids": ids})


def product_video_list(*, product_id: str, page_num: int = 1, page_size: int = 10) -> list[dict[str, Any]]:
    return _list_data(
        f"{API_PREFIX}/product/video/list",
        params={
            "product_id": product_id,
            "page_num": page_num,
            "page_size": min(10, max(1, page_size)),
        },
    )


def product_influencer_list(*, product_id: str, page_num: int = 1, page_size: int = 10) -> list[dict[str, Any]]:
    return _list_data(
        f"{API_PREFIX}/product/influencer/list",
        params={
            "product_id": product_id,
            "page_num": page_num,
            "page_size": min(10, max(1, page_size)),
        },
    )


def product_trend(
    *,
    product_id: str,
    start_date: str,
    end_date: str,
    page_num: int = 1,
    page_size: int = 10,
) -> list[dict[str, Any]]:
    return _list_data(
        f"{API_PREFIX}/product/trend",
        params={
            "product_id": product_id,
            "start_date": start_date,
            "end_date": end_date,
            "page_num": page_num,
            "page_size": min(10, max(1, page_size)),
        },
    )


def video_detail(video_ids: list[str]) -> list[dict[str, Any]]:
    ids = ",".join(i.strip() for i in video_ids if i.strip())[:500]
    if not ids:
        return []
    return _list_data(f"{API_PREFIX}/video/detail", params={"video_ids": ids})


def seller_detail(seller_id: str) -> dict[str, Any] | None:
    body = _get(f"{API_PREFIX}/seller/detail", params={"seller_id": seller_id})
    data = body.get("data")
    return data if isinstance(data, dict) else None
