"""Download EchoTik product cover images for Kling renders."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx

from shorts_bot.config import settings

# Padding color when fitting product into 9:16 (neutral studio gray — Kling replaces backdrop)
_FIT_PAD_RGB = (42, 42, 44)


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


def prepare_vertical_9x16(
    image_bytes: bytes,
    *,
    width: int = 1080,
    height: int = 1920,
    fit_scale: float | None = None,
) -> bytes:
    """
    Fit product image inside 9:16 with padding (zoom out).
    Course + Moe: avoid tight center-crop that makes clips feel too zoomed in.
    """
    from io import BytesIO

    from PIL import Image

    scale = fit_scale if fit_scale is not None else float(settings.tiktok_shop_image_fit_scale or 0.88)
    scale = max(0.5, min(1.0, scale))

    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    max_w = int(width * scale)
    max_h = int(height * scale)
    resize_scale = min(max_w / w, max_h / h)
    new_w = max(1, int(w * resize_scale))
    new_h = max(1, int(h * resize_scale))
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (width, height), _FIT_PAD_RGB)
    left = (width - new_w) // 2
    top = (height - new_h) // 2
    canvas.paste(img, (left, top))

    out = BytesIO()
    canvas.save(out, format="JPEG", quality=92)
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
