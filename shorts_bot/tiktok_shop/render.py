"""Render TikTok Shop product clips via Kling."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop import kling_client
from shorts_bot.tiktok_shop.product_images import download_cover, image_payload_for_kling, parse_cover_url
from shorts_bot.tiktok_shop.product_scout import load_products
from shorts_bot.tiktok_shop.video_variants import make_pan_loop_clip


# Tell Kling to avoid the empty gray void / unfinished 3D look.
NEGATIVE_PROMPT = (
    "empty void, plain gray background, unfinished 3D render, blender default scene, "
    "featureless backdrop, flat monochrome wall, low quality, blur, distortion, text, watermark"
)

DEFAULT_PROMPT = (
    "Finished e-commerce product shot: item centered on a polished studio surface with "
    "soft warm gradient backdrop and subtle props, professional three-point lighting, "
    "real shadow and reflection, vertical TikTok Shop ad, no text overlays, no people"
)

# Kling background / set dressing — pick per product type (not one void-fits-all).
PROMPT_STYLES: dict[str, str] = {
    "studio": DEFAULT_PROMPT,
    "vanity": (
        "Finished luxury beauty ad: product on marble vanity tray with soft warm bathroom "
        "lighting, blurred boutique mirror and cosmetics bokeh behind, high-end shelf styling, "
        "vertical TikTok Shop, no text, no people"
    ),
    "lifestyle": (
        "Finished lifestyle product ad: item on styled home countertop or shelf, natural "
        "window light, cozy modern interior softly blurred behind, lived-in decor cues, "
        "vertical TikTok Shop, no text, no people"
    ),
    "minimal": (
        "Finished premium product photography: item on seamless white infinity backdrop with "
        "soft studio shadow and gentle gradient falloff, Apple-style commercial look, "
        "vertical TikTok Shop, no text, no people"
    ),
}

_BEAUTY_KEYWORDS = (
    "lip", "lipstick", "balm", "gloss", "makeup", "serum", "cream", "beauty",
    "skincare", "mascara", "eyeliner", "cosmetic", "perfume",
)
_HOME_KEYWORDS = (
    "mug", "cup", "towel", "pillow", "blanket", "home", "kitchen", "decor",
    "candle", "organizer",
)
_APPAREL_KEYWORDS = ("shirt", "tee", "hoodie", "apparel", "wear", "dress", "hat")


def suggest_style(product_name: str) -> str:
    """Pick a background style from product title keywords."""
    name = (product_name or "").lower()
    if any(k in name for k in _BEAUTY_KEYWORDS):
        return "vanity"
    if any(k in name for k in _HOME_KEYWORDS):
        return "lifestyle"
    if any(k in name for k in _APPAREL_KEYWORDS):
        return "lifestyle"
    return "studio"


def prompt_for_style(style: str, *, product_name: str = "") -> str:
    key = (style or "").strip().lower()
    if key in ("auto", ""):
        key = suggest_style(product_name)
    return PROMPT_STYLES.get(key, DEFAULT_PROMPT)


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
    printify_id: str = "",
    printify_title: str = "",
    image_url: str = "",
    image_path: Path | None = None,
    prompt: str = "",
    style: str = "auto",
    loop: bool = True,
    skip_if_exists: bool = True,
) -> RenderResult:
    if not kling_client.configured():
        raise RuntimeError("Kling not configured — add KLING_ACCESS_KEY + KLING_SECRET_KEY to Secrets")

    row: dict = {}
    if printify_id or printify_title:
        from shorts_bot.tiktok_shop import printify_client

        pf = printify_client.find_product(product_id=printify_id, title=printify_title)
        product_name = product_name or str(pf.get("title") or "")
        product_id = product_id or str(pf.get("id") or "")
        image_url = image_url or printify_client.hero_image_url(pf)
        if not image_url:
            raise RuntimeError(f"Printify product has no mockup image: {product_name}")
    elif product_id or product_name:
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
        download_cover(product_id=product_id, cover_url=image_url)

    try:
        image_for_kling = image_payload_for_kling(product_id=product_id, cover_url=image_url)
    except RuntimeError as exc:
        raise RuntimeError(str(exc)) from exc

    out_dir = clips_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(product_name or product_id)
    raw = out_dir / f"{slug}_raw.mp4"
    loop_path = out_dir / f"{slug}_loop.mp4"

    if skip_if_exists and raw.is_file() and raw.stat().st_size > 10_000:
        task_id = "cached"
    else:
        kling_prompt = prompt or prompt_for_style(style, product_name=product_name)
        task_id = kling_client.create_image2video(
            image_url=image_for_kling,
            prompt=kling_prompt,
            negative_prompt=NEGATIVE_PROMPT,
            duration=5,
            mode=(settings.kling_mode or "std").strip().lower(),  # std=720p (cheaper; use pro when scaling)
            aspect_ratio="9:16",
            sound="off",
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
