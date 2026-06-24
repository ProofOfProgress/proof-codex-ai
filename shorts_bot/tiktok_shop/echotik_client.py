"""EchoTik API client — TikTok Shop product research."""

from __future__ import annotations

import base64
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
    body = _get(
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
    data = body.get("data")
    return data if isinstance(data, list) else []


def product_detail(product_ids: list[str]) -> list[dict[str, Any]]:
    ids = ",".join(i.strip() for i in product_ids if i.strip())[:500]
    if not ids:
        return []
    body = _get(f"{API_PREFIX}/product/detail", params={"product_ids": ids})
    data = body.get("data")
    return data if isinstance(data, list) else []
