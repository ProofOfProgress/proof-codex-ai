"""Route image generation to configured paid provider."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.images.fal import generate_fal_image
from shorts_bot.production.images.replicate import generate_replicate_image


def generate_image(prompt: str, out_path: Path) -> str:
    provider = (settings.image_provider or "replicate").strip().lower()

    if provider == "fal":
        if not settings.has_fal_images:
            raise ValueError("FAL_API_KEY not set.")
        return generate_fal_image(
            prompt,
            out_path,
            api_key=settings.fal_api_key or "",
            model=settings.fal_image_model,
        )

    if settings.has_replicate_images:
        return generate_replicate_image(
            prompt,
            out_path,
            token=settings.replicate_api_token or "",
            model=settings.replicate_image_model,
            aspect_ratio=settings.image_aspect_ratio,
        )

    if settings.has_fal_images:
        return generate_fal_image(
            prompt,
            out_path,
            api_key=settings.fal_api_key or "",
            model=settings.fal_image_model,
        )

    raise ValueError(
        "No image API configured. Set REPLICATE_API_TOKEN or FAL_API_KEY in Cursor Secrets."
    )
