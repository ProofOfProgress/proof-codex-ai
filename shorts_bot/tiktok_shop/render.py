"""Render TikTok Shop product clips via Kling."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop import kling_client
from shorts_bot.tiktok_shop.product_images import download_cover, parse_cover_url
from shorts_bot.tiktok_shop.product_scout import load_products
from shorts_bot.tiktok_shop.video_variants import make_pan_loop_clip


DEFAULT_PROMPT = (
    "Slow cinematic pan and zoom on product, clean e-commerce lighting, "
    "minimal background, vertical TikTok Shop ad style, no text overlays, no people"
)


@dataclass
class RenderResult:
    product_id: str
    product_name: str
    raw_mp4: Path
    loop_mp4: Path | None
    task_id: str


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", name.lower()).strip("_")
    return slug[:48] or "product"


def clips_dir() -> Path:
    return settings.data_dir / "tiktok_shop" / "clips"


def render_product_clip(
    *,
    product_id: str = "",
    product_name: str = "",
    image_url: str = "",
    image_path: Path | None = None,
    prompt: str = "",
    loop: bool = True,
    skip_if_exists: bool = True,
) -> RenderResult:
    if not kling_client.configured():
        raise RuntimeError("Kling not configured — add KLING_API_KEY to Secrets")

    row: dict = {}
    if product_id or product_name:
        for p in load_products():
            if product_id and str(p.get("product_id")) == product_id:
                row = p
                break
            if product_name and product_name.lower() in str(p.get("product_name", "")).lower():
                row = p
                break
    if row:
        product_id = product_id or str(row.get("product_id") or "")
        product_name = product_name or str(row.get("product_name") or "")
        image_url = image_url or str(row.get("cover_url") or "")

    if image_path is None and product_id and parse_cover_url(image_url):
        image_path = download_cover(product_id=product_id, cover_url=image_url)

    url = parse_cover_url(image_url)
    if not url:
        raise RuntimeError("Kling needs a public image URL — run: factory_cli prep-images --force")
    image_for_kling = url
    if image_path is None and product_id:
        download_cover(product_id=product_id, cover_url=image_url)

    out_dir = clips_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(product_name or product_id)
    raw = out_dir / f"{slug}_raw.mp4"
    loop_path = out_dir / f"{slug}_loop.mp4"

    if skip_if_exists and raw.is_file() and raw.stat().st_size > 10_000:
        task_id = "cached"
    else:
        task_id = kling_client.create_image2video(
            image_url=image_for_kling,
            prompt=prompt or DEFAULT_PROMPT,
            duration=5,
        )
        video_url = kling_client.wait_for_video_url(task_id)
        kling_client.download_video(video_url, raw)

    loop_out: Path | None = None
    if loop:
        if skip_if_exists and loop_path.is_file() and loop_path.stat().st_size > 10_000:
            loop_out = loop_path
        else:
            loop_out = make_pan_loop_clip(raw, loop_path)

    return RenderResult(
        product_id=product_id,
        product_name=product_name,
        raw_mp4=raw,
        loop_mp4=loop_out,
        task_id=task_id,
    )
