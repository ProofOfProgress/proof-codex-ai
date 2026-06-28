"""Module 4 image generation — Gemini Nano Banana Pro (course defaults)."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.images.gemini import generate_gemini_image
from shorts_bot.production.images.router import generate_image

# Course Module 4 — Higgsfield NanoBanana settings (via Gemini API).
DEFAULT_MODEL = "gemini-3-pro-image-preview"
FAST_MODEL = "gemini-3.1-flash-image-preview"

_COURSE_RULES = (
    "TikTok Shop affiliate product image (Module 4). Photorealistic e-commerce ad. "
    "Vertical 9:16 composition. Accurate product scale and materials. "
    "Professional studio or lifestyle staging as described. "
    "No watermark, no TikTok UI, no illegible text unless the prompt asks for on-image text. "
    "No sale/price/discount words on the image."
)


def images_dir() -> Path:
    return settings.data_dir / "tiktok_shop" / "images"


def enrich_prompt(prompt: str) -> str:
    """Wrap owner/GPT prompt with course Module 4 constraints."""
    body = (prompt or "").strip()
    if not body:
        raise ValueError("Image prompt is empty — paste ChatGPT Prompt Builder output.")
    return f"{_COURSE_RULES}\n\n{body}"


def generate_product_image(
    prompt: str,
    out_path: Path | None = None,
    *,
    slug: str = "product",
    reference_images: list[Path] | None = None,
    product_images: list[Path] | None = None,
    fast: bool = False,
) -> Path:
    """
  Generate a Module 4 product image.

  Reference images (in-context scale) should be listed first; isolated product shots after.
  """
    refs: list[Path] = []
    for group in (reference_images, product_images):
        if group:
            refs.extend([p for p in group if p.is_file()])

    dest = out_path or images_dir() / f"{slug}.png"
    full_prompt = enrich_prompt(prompt)
    provider = (settings.image_provider or "gemini").strip().lower()

    if provider == "gemini" or settings.has_gemini:
        if not settings.has_gemini:
            raise RuntimeError("GEMINI_API_KEY not set — add in Cursor Cloud Agent secrets.")
        model = settings.gemini_image_model or DEFAULT_MODEL
        if fast:
            model = settings.gemini_image_fast_model or FAST_MODEL
        generate_gemini_image(
            full_prompt,
            dest,
            api_key=settings.gemini_api_key or "",
            model=model,
            aspect_ratio=settings.image_aspect_ratio or "9:16",
            image_size=settings.gemini_image_size or "2K",
            reference_images=refs or None,
        )
        return dest

    generate_image(full_prompt, dest)
    return dest
