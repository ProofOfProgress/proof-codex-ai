"""Render TikTok Shop product clips via Kling."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop import kling_client
from shorts_bot.tiktok_shop.pipeline import load_prompt_file, validate_before_render
from shorts_bot.tiktok_shop.product_images import download_cover, image_payload_for_kling, parse_cover_url
from shorts_bot.tiktok_shop.product_scout import load_products
from shorts_bot.tiktok_shop.video_variants import make_pan_loop_clip

# Kling negative — ban gray letterbox, static stills, plain void
NEGATIVE_PROMPT = (
    "empty void, plain gray background, gray border, letterbox bars, black bars, padded frame, "
    "unfinished 3D render, blender default scene, featureless backdrop, flat monochrome wall, "
    "plain white box, isolated product on white, static photograph, frozen still image, "
    "no camera motion, locked tripod, product moving, product rotating, "
    "phone screen, mobile app icons, home screen UI, laptop screen with UI, MacBook logo, "
    "Apple logo, Instagram logo, third-party brand logos, competitor branding, "
    "low quality, blur, distortion, text, watermark, extreme close-up, tight crop, product fills entire frame"
)

# Fallback only when --allow-default-prompt (tests / emergency)
DEFAULT_PROMPT = (
    "Use the uploaded product image as the exact reference. Realistic UGC-style TikTok Shop product "
    "video on a styled kitchen counter with warm wood grain, soft window light, blurred mugs and "
    "herbs in the background — not a plain white listing box. Product centered, fully in frame, "
    "completely stationary. Handheld phone camera with iPhone 0.5x ultra-wide feel. Slow subtle "
    "multi-axis arc around the product with slight handheld micro-shake — camera moves, product does "
    "not. Soft natural light, grounded shadows, realistic reflections. Vertical 9:16 framing. "
    "No people, no text overlays, no sale signage."
)

ARC_CAMERA_SUFFIX = (
    " Arc camera shot from left to right with gentle handheld micro-shake — product stays "
    "stationary in center; camera moves in a smooth organic arc, not static."
)

PROMPT_STYLES: dict[str, str] = {
    "studio": DEFAULT_PROMPT,
    "vanity": (
        "Use uploaded image as exact reference. Luxury beauty ad on marble vanity with brushed "
        "gold tray, soft warm bathroom light, blurred boutique mirror and cosmetics bokeh behind — "
        "rich staged background, not plain white. Product stationary, centered, in frame entire "
        "clip. Handheld phone arc camera with slight micro-shake. Vertical 9:16 TikTok Shop."
    ),
    "lifestyle": (
        "Use uploaded image as exact reference. Lifestyle product ad on styled home countertop "
        "with natural window light, plants and decor softly blurred behind — complex believable "
        "environment. Product stationary; slow multi-axis arc camera with handheld micro-shake. "
        "Vertical 9:16 TikTok Shop."
    ),
    "kitchen": (
        "Use uploaded image as exact reference. Kitchen counter scene with tile backsplash, warm "
        "ambient light, subtle props blurred in depth — not a white void. Product stationary; "
        "arc camera with organic handheld drift. Vertical 9:16."
    ),
}

_BEAUTY_KEYWORDS = (
    "lip", "lipstick", "balm", "gloss", "makeup", "serum", "cream", "beauty",
    "skincare", "mascara", "eyeliner", "cosmetic", "perfume",
)
_HOME_KEYWORDS = (
    "mug", "cup", "towel", "pillow", "blanket", "home", "kitchen", "decor",
    "candle", "organizer", "tumbler", "mount",
)
_APPAREL_KEYWORDS = ("shirt", "tee", "hoodie", "apparel", "wear", "dress", "hat")


def suggest_style(product_name: str) -> str:
    name = (product_name or "").lower()
    if any(k in name for k in _BEAUTY_KEYWORDS):
        return "vanity"
    if any(k in name for k in _HOME_KEYWORDS):
        return "kitchen"
    if any(k in name for k in _APPAREL_KEYWORDS):
        return "lifestyle"
    return "studio"


def prompt_for_style(style: str, *, product_name: str = "") -> str:
    key = (style or "").strip().lower()
    if key in ("auto", ""):
        key = suggest_style(product_name)
    if key == "minimal":
        key = "kitchen"  # plain white box retired — increases still-image ban risk
    return PROMPT_STYLES.get(key, DEFAULT_PROMPT)


@dataclass
class RenderResult:
    product_id: str
    product_name: str
    raw_mp4: Path
    loop_mp4: Path | None
    task_id: str
    prompt_used: str


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", name.lower()).strip("_")
    return slug[:48] or "product"


def clips_dir() -> Path:
    return settings.data_dir / "tiktok_shop" / "clips"


def resolve_kling_image(
    *,
    product_name: str,
    image_path: Path | None = None,
    use_sample: bool = True,
) -> Path:
    """Prefer Gemini Module 4 sample; fall back to explicit --image path."""
    if image_path is not None and Path(image_path).is_file():
        return Path(image_path)
    if use_sample and product_name:
        from shorts_bot.tiktok_shop.module4_sample import sample_image_path

        sample = sample_image_path(product_name)
        if sample.is_file():
            return sample
    if image_path is not None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    raise RuntimeError(
        f"No Kling input image for {product_name or 'product'}. "
        "Run: factory_cli sample-image --product NAME --source LISTING.jpg"
    )


def _resolve_kling_prompt(
    *,
    prompt: str,
    prompt_file: Path | None,
    style: str,
    product_name: str,
    allow_default_prompt: bool,
) -> str:
    text = (prompt or "").strip()
    if prompt_file and Path(prompt_file).is_file():
        text = load_prompt_file(prompt_file)
    if text:
        if "arc" not in text.lower() and "camera" not in text.lower():
            text = text.rstrip(".") + "." + ARC_CAMERA_SUFFIX
        return text
    if allow_default_prompt:
        return prompt_for_style(style, product_name=product_name) + ARC_CAMERA_SUFFIX
    raise RuntimeError(
        "Kling prompt required — delegate to product-video-prompt-builder first.\n"
        "  python3 -m shorts_bot.tiktok_shop.factory_cli prompt-dispatch --product \"NAME\" "
        "--product-image PATH [--reference-image PATH]\n"
        "Then save prompt and render:\n"
        "  factory_cli save-prompt --product \"NAME\" --prompt \"...\"\n"
        "  factory_cli render --product \"NAME\" --image PATH --prompt-file data/tiktok_shop/prompts/NAME.kling.txt"
    )


def render_product_clip(
    *,
    product_id: str = "",
    product_name: str = "",
    printify_id: str = "",
    printify_title: str = "",
    image_url: str = "",
    image_path: Path | None = None,
    listing_image: Path | None = None,
    reference_image: Path | None = None,
    use_sample: bool = True,
    prompt: str = "",
    prompt_file: Path | None = None,
    style: str = "auto",
    loop: bool = True,
    on_screen_caption: str = "",
    skip_if_exists: bool = True,
    allow_default_prompt: bool = False,
    validate_pipeline: bool = True,
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

    kling_prompt = _resolve_kling_prompt(
        prompt=prompt,
        prompt_file=prompt_file,
        style=style,
        product_name=product_name,
        allow_default_prompt=allow_default_prompt,
    )

    kling_image = resolve_kling_image(
        product_name=product_name,
        image_path=image_path,
        use_sample=use_sample,
    )
    ref_for_validate = reference_image or listing_image

    if validate_pipeline:
        check = validate_before_render(
            product_name=product_name,
            product_image=kling_image,
            reference_image=ref_for_validate,
            prompt_text=kling_prompt,
        )
        if check.warnings:
            import sys

            for w in check.warnings:
                print(f"Pipeline warning: {w}", file=sys.stderr)
        if not check.ok:
            raise RuntimeError("; ".join(check.errors))

    try:
        import base64

        from shorts_bot.tiktok_shop.product_images import prepare_vertical_9x16

        if kling_image.is_file():
            data = prepare_vertical_9x16(kling_image.read_bytes())
        elif product_id or parse_cover_url(image_url):
            image_for_kling = image_payload_for_kling(product_id=product_id, cover_url=image_url)
            data = None
        else:
            raise RuntimeError(f"No Kling input image for {product_name or product_id}")

        if data is not None:
            if len(data) > 10 * 1024 * 1024:
                raise RuntimeError("Product image exceeds Kling 10MB limit")
            image_for_kling = base64.standard_b64encode(data).decode("ascii")
    except RuntimeError as exc:
        raise RuntimeError(str(exc)) from exc

    out_dir = clips_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(product_name or product_id)
    raw = out_dir / f"{slug}_raw.mp4"
    loop_path = out_dir / f"{slug}_loop.mp4"
    final_path = out_dir / f"{slug}_final.mp4"

    if skip_if_exists and raw.is_file() and raw.stat().st_size > 10_000:
        task_id = "cached"
    else:
        task_id = kling_client.create_image2video(
            image_url=image_for_kling,
            prompt=kling_prompt,
            negative_prompt=NEGATIVE_PROMPT,
            duration=5,
            mode=(settings.kling_mode or "std").strip().lower(),
            aspect_ratio=kling_client.REQUIRED_ASPECT_RATIO,
            model_name=kling_client.resolve_model_name(),
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

    caption_text = (on_screen_caption or "").strip()
    if loop_out and caption_text:
        delivery = (settings.tiktok_shop_hook_delivery or "native").strip().lower()
        if delivery == "burn_in":
            from shorts_bot.tiktok_shop.video_editor import burn_on_screen_caption

            if skip_if_exists and final_path.is_file() and final_path.stat().st_size > 10_000:
                loop_out = final_path
            else:
                loop_out = burn_on_screen_caption(loop_out, final_path, caption_text)
        else:
            from shorts_bot.tiktok_shop.captions import save_hook_sidecar

            save_hook_sidecar(loop_out, caption_text)

    return RenderResult(
        product_id=product_id,
        product_name=product_name,
        raw_mp4=raw,
        loop_mp4=loop_out,
        task_id=task_id,
        prompt_used=kling_prompt,
    )
