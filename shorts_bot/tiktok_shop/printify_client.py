"""Printify REST API — list shops/products, mockup images for Kling clips."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from shorts_bot.config import settings

API_BASE = "https://api.printify.com/v1"
USER_AGENT = "ShortsBot-TikTokShop/1.0"


def configured() -> bool:
    token = (settings.printify_api_token or "").strip()
    if not token:
        return False
    lower = token.lower()
    return "placeholder" not in lower and "your-" not in lower


def _headers() -> dict[str, str]:
    token = (settings.printify_api_token or "").strip()
    if not token:
        raise RuntimeError("Printify not configured — set PRINTIFY_API_TOKEN in Secrets")
    return {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json;charset=utf-8",
    }


def _request(method: str, path: str, **kwargs) -> Any:
    url = f"{API_BASE}{path}"
    with httpx.Client(timeout=60.0) as client:
        resp = client.request(method, url, headers=_headers(), **kwargs)
    if resp.status_code >= 400:
        raise RuntimeError(f"Printify error ({resp.status_code}): {resp.text[:300]}")
    if resp.status_code == 204 or not resp.content:
        return {}
    return resp.json()


def list_shops() -> list[dict[str, Any]]:
    body = _request("GET", "/shops.json")
    if isinstance(body, list):
        return body
    return []


def resolve_shop_id() -> str:
    explicit = (settings.printify_shop_id or "").strip()
    if explicit:
        return explicit
    shops = list_shops()
    if not shops:
        raise RuntimeError("Printify: no shops on account — connect TikTok Shop in Printify first")
    shop_id = shops[0].get("id")
    if shop_id is None:
        raise RuntimeError("Printify: could not read shop id")
    return str(shop_id)


def list_products(*, shop_id: str | None = None, page: int = 1, limit: int = 50) -> list[dict[str, Any]]:
    sid = shop_id or resolve_shop_id()
    body = _request("GET", f"/shops/{sid}/products.json", params={"page": page, "limit": limit})
    if isinstance(body, dict):
        data = body.get("data")
        if isinstance(data, list):
            return data
    if isinstance(body, list):
        return body
    return []


def get_product(product_id: str, *, shop_id: str | None = None) -> dict[str, Any]:
    sid = shop_id or resolve_shop_id()
    body = _request("GET", f"/shops/{sid}/products/{product_id.strip()}.json")
    return body if isinstance(body, dict) else {}


def hero_image_url(product: dict[str, Any]) -> str:
    """Best mockup URL for Kling — prefers front / first image."""
    images = product.get("images") or []
    if not isinstance(images, list):
        return ""

    def _src(img: object) -> str:
        if isinstance(img, dict):
            return str(img.get("src") or img.get("url") or "").strip()
        return ""

    for preferred in ("front", "other"):
        for img in images:
            if not isinstance(img, dict):
                continue
            pos = str(img.get("position") or img.get("camera_label") or "").lower()
            if preferred == "front" and "front" in pos:
                url = _src(img)
                if url:
                    return url
    for img in images:
        url = _src(img)
        if url:
            return url
    return ""


def products_cache_path() -> Path:
    return settings.data_dir / "tiktok_shop" / "printify_products.json"


def sync_products(*, shop_id: str | None = None) -> Path:
    rows: list[dict[str, Any]] = []
    page = 1
    while True:
        batch = list_products(shop_id=shop_id, page=page, limit=50)
        if not batch:
            break
        for row in batch:
            rows.append(
                {
                    "printify_id": str(row.get("id") or ""),
                    "title": str(row.get("title") or "").strip(),
                    "description": str(row.get("description") or "")[:500],
                    "visible": row.get("visible"),
                    "hero_image": hero_image_url(row),
                    "tags": row.get("tags") or [],
                }
            )
        if len(batch) < 50:
            break
        page += 1

    path = products_cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return path


def load_cached_products() -> list[dict[str, Any]]:
    path = products_cache_path()
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def find_product(*, product_id: str = "", title: str = "") -> dict[str, Any]:
    pid = product_id.strip()
    if pid and configured():
        return get_product(pid)

    needle = title.strip().lower()
    if needle:
        for row in load_cached_products():
            if needle in str(row.get("title") or "").lower():
                if pid := str(row.get("printify_id") or ""):
                    return get_product(pid)
        if configured():
            for row in list_products(limit=100):
                if needle in str(row.get("title") or "").lower():
                    return row

    raise RuntimeError(f"Printify product not found: {product_id or title!r} — run printify_cli sync")
