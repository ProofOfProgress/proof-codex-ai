"""Download EchoTik product cover images for Kling renders."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx

from shorts_bot.config import settings


def parse_cover_url(raw: object) -> str:
    """EchoTik cover_url is often a JSON list of {url, index} objects."""
    if not raw:
        return ""
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict) and item.get("url"):
                return str(item["url"]).strip()
        return ""
    text = str(raw).strip()
    if not text:
        return ""
    if text.startswith("["):
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            pass
        else:
            return parse_cover_url(data)
    m = re.search(r"https?://[^\s\"'\]}]+", text)
    return m.group(0) if m else text


def image_path_for_product(product_id: str, *, ext: str = ".jpg") -> Path:
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", product_id.strip())[:80]
    return settings.data_dir / "tiktok_shop" / "images" / f"{safe}{ext}"


def _ext_from_url(url: str) -> str:
    path = urlparse(url).path.lower()
    for ext in (".jpeg", ".jpg", ".png", ".webp"):
        if path.endswith(ext):
            return ".jpg" if ext == ".jpeg" else ext
    return ".jpg"


def download_cover(*, product_id: str, cover_url: str, force: bool = False) -> Path | None:
    url = parse_cover_url(cover_url)
    if not url:
        raise RuntimeError(f"No cover URL for product {product_id}")
    dest = image_path_for_product(product_id, ext=_ext_from_url(url))
    if dest.is_file() and not force:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ShortsBot/1.0)",
        "Referer": "https://echotik.live/",
    }
    try:
        with httpx.Client(timeout=60.0, follow_redirects=True, headers=headers) as client:
            resp = client.get(url)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
    except httpx.HTTPStatusError as exc:
        # EchoTik CDN often blocks server downloads; Kling uses the URL directly.
        if exc.response.status_code in {403, 401}:
            return None
        raise
    return dest


def download_for_products(products: list[dict], *, force: bool = False) -> list[Path]:
    paths: list[Path] = []
    skipped = 0
    for row in products:
        pid = str(row.get("product_id") or "").strip()
        url = row.get("cover_url") or ""
        if not pid or not parse_cover_url(url):
            continue
        result = download_cover(product_id=pid, cover_url=str(url), force=force)
        if result is None:
            skipped += 1
            continue
        paths.append(result)
    if skipped:
        import sys

        print(
            f"Note: {skipped} image(s) blocked by EchoTik CDN (403) — "
            "Kling render still uses the public cover URL.",
            file=sys.stderr,
        )
    return paths
