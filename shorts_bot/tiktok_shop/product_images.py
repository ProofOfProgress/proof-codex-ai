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


def tiktok_cdn_url_from_detail(row: dict) -> str:
    """First TikTok CDN variant image from EchoTik sale_props (public, Kling-friendly)."""
    props_raw = row.get("sale_props") or ""
    try:
        props = json.loads(props_raw) if isinstance(props_raw, str) else props_raw
    except json.JSONDecodeError:
        props = []
    if not isinstance(props, list):
        return ""
    for prop in props:
        if not isinstance(prop, dict):
            continue
        for val in prop.get("sale_prop_values") or []:
            if not isinstance(val, dict):
                continue
            img = str(val.get("image") or "").strip()
            if img and ("ttcdn" in img or "tiktokcdn" in img):
                return img
    return ""


def load_image_bytes_for_kling(*, product_id: str = "", cover_url: str = "") -> bytes:
    """Download a product image Kling can use (TikTok CDN preferred over EchoTik CDN)."""
    from shorts_bot.tiktok_shop import echotik_client

    if product_id and echotik_client.configured():
        details = echotik_client.product_detail([product_id])
        if details:
            cdn = tiktok_cdn_url_from_detail(details[0])
            if cdn:
                with httpx.Client(timeout=60.0, follow_redirects=True) as client:
                    resp = client.get(cdn)
                    resp.raise_for_status()
                    return resp.content

    for candidate in (parse_cover_url(cover_url), cover_url):
        url = parse_cover_url(candidate)
        if not url:
            continue
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ShortsBot/1.0)",
            "Referer": "https://www.tiktok.com/",
        }
        try:
            with httpx.Client(timeout=60.0, follow_redirects=True, headers=headers) as client:
                resp = client.get(url)
                resp.raise_for_status()
                return resp.content
        except httpx.HTTPStatusError:
            continue

    raise RuntimeError(
        f"No downloadable product image for {product_id or cover_url[:40]} — "
        "run prep-images --force after scout"
    )


def prepare_vertical_9x16(image_bytes: bytes, *, width: int = 1080, height: int = 1920) -> bytes:
    """Center-crop to 9:16 and resize for TikTok vertical (Kling + phone feed)."""
    from io import BytesIO

    from PIL import Image

    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    target_ratio = 9 / 16
    current = w / h
    if current > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    out = BytesIO()
    img.save(out, format="JPEG", quality=92)
    return out.getvalue()


def image_payload_for_kling(*, product_id: str = "", cover_url: str = "") -> str:
    """Raw base64 for Kling image2video (no data: prefix)."""
    import base64

    data = prepare_vertical_9x16(load_image_bytes_for_kling(product_id=product_id, cover_url=cover_url))
    if len(data) > 10 * 1024 * 1024:
        raise RuntimeError("Product image exceeds Kling 10MB limit")
    return base64.standard_b64encode(data).decode("ascii")


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
