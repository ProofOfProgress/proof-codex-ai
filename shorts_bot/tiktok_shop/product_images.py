"""Download product cover images for Kling renders."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import httpx
from PIL import Image

from shorts_bot.config import settings

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
ASPECT_9_16 = 9 / 16
ASPECT_TOLERANCE = 0.025


@dataclass
class ImageValidation:
    ok: bool
    width: int = 0
    height: int = 0
    aspect_ratio: float = 0.0
    is_9_16: bool = False
    plain_background_risk: bool = False
    errors: list[str] | None = None
    warnings: list[str] | None = None

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


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


def _sample_border_uniformity(img: Image.Image, *, samples: int = 24) -> float:
    """Return 0–1 score — high = uniform border (plain white/gray box risk)."""
    w, h = img.size
    if w < 20 or h < 20:
        return 0.0
    pts = []
    for x in range(0, w, max(1, w // 6)):
        pts.extend([(x, 0), (x, h - 1), (0, x), (w - 1, x)])
    pts = pts[:samples]
    colors = [img.getpixel(p)[:3] if isinstance(img.getpixel(p), tuple) else img.getpixel(p) for p in pts]
    if not colors:
        return 0.0
    avg = tuple(sum(c[i] for c in colors) / len(colors) for i in range(3))
    var = sum(sum((c[i] - avg[i]) ** 2 for i in range(3)) for c in colors) / len(colors)
    bright = sum(1 for c in colors if sum(c) / 3 > 230) / len(colors)
    if var < 400 and bright > 0.7:
        return 0.9
    if var < 900 and bright > 0.5:
        return 0.6
    return 0.0


def validate_module4_image(image_bytes: bytes) -> ImageValidation:
    """Check Module 4 still before Kling — must be full-bleed 9:16, not plain listing box."""
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    ratio = w / h if h else 0.0
    is_916 = abs(ratio - ASPECT_9_16) <= ASPECT_TOLERANCE
    result = ImageValidation(
        ok=True,
        width=w,
        height=h,
        aspect_ratio=round(ratio, 4),
        is_9_16=is_916,
    )
    if w < 720 or h < 1280:
        result.warnings.append(f"Low resolution {w}x{h} — Module 4 should be 2K 9:16 when possible")
    if not is_916:
        result.warnings.append(
            f"Source aspect {w}x{h} is not 9:16 — will center-crop to 9:16 (no gray letterbox)"
        )
    plain = _sample_border_uniformity(img)
    if plain >= 0.6:
        result.plain_background_risk = True
        result.warnings.append(
            "Plain white/gray background detected — use a staged Module 4 scene (complex backdrop) "
            "to reduce still-image ban risk and show arc camera motion"
        )
    result.ok = not result.errors
    return result


def prepare_vertical_9x16(
    image_bytes: bytes,
    *,
    width: int = TARGET_WIDTH,
    height: int = TARGET_HEIGHT,
    fit_scale: float | None = None,
) -> bytes:
    """
    Full-bleed 9:16 for Kling input — **no gray letterbox bars**.

    - Already ~9:16: resize to target
    - Other aspects: center cover-crop then resize (product fills frame)
    """
    _ = fit_scale  # legacy param — cover crop replaces padded letterbox

    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    target_ratio = width / height
    src_ratio = w / h if h else target_ratio

    if abs(src_ratio - target_ratio) <= ASPECT_TOLERANCE:
        out_img = img.resize((width, height), Image.Resampling.LANCZOS)
    else:
        if src_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))
        out_img = img.resize((width, height), Image.Resampling.LANCZOS)

    out = BytesIO()
    out_img.save(out, format="JPEG", quality=92)
    return out.getvalue()


# Legacy name kept for tests importing _FIT_PAD_RGB — cover crop no longer pads
_FIT_PAD_RGB = (42, 42, 44)


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
