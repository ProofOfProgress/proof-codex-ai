"""Module 4 — Gemini sample image (9:16 full-bleed) for Kling input.

Owner pipeline tip: send listing product photo to Gemini → get a staged 9:16
sample with full product visible → feed *that* to Kling + prompt-builder prompt.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from shorts_bot.config import settings

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920


@dataclass
class SampleImageResult:
    product_name: str
    source_image: str
    sample_path: Path
    width: int
    height: int
    model: str
    prompt_used: str


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", name.lower()).strip("_")
    return slug[:48] or "product"


def samples_dir() -> Path:
    return settings.data_dir / "tiktok_shop" / "samples"


def sample_image_path(product_name: str) -> Path:
    return samples_dir() / f"{_slug(product_name)}_916.jpg"


def _require_gemini_client():
    if not settings.has_gemini:
        raise RuntimeError("GEMINI_API_KEY required for Module 4 sample images — add in Cursor Secrets")
    from google import genai

    return genai.Client(api_key=settings.gemini_api_key)


def _scene_hint(product_name: str, style: str = "auto") -> str:
    from shorts_bot.tiktok_shop.render import suggest_style

    key = suggest_style(product_name) if style in ("auto", "") else style.strip().lower()
    hints = {
        "vanity": "marble bathroom vanity with soft warm light and blurred mirror bokeh",
        "kitchen": "styled kitchen counter with warm wood grain and tile backsplash depth",
        "lifestyle": "home shelf or countertop with cozy decor softly blurred behind",
        "studio": "premium studio surface with soft gradient backdrop and subtle props",
    }
    return hints.get(key, hints["kitchen"])


def build_sample_prompt(
    *,
    product_name: str,
    style: str = "auto",
    reference_note: bool = False,
) -> str:
    scene = _scene_hint(product_name, style)
    ref = (
        " Use the optional reference image only for real-world scale — not for copying its plain backdrop."
        if reference_note
        else ""
    )
    return (
        f"Use the uploaded product photo as the exact product reference.{ref} "
        f"Create a photorealistic TikTok Shop product still for: {product_name.strip() or 'this product'}. "
        "Vertical 9:16 aspect ratio, full frame edge-to-edge — NO letterbox bars, NO gray or black borders, "
        "NO empty padding. Product must be fully visible, centered, correct scale, and sharp. "
        f"Place the product in a rich staged scene: {scene}. "
        "Soft natural lighting with matching shadows on product and surface. "
        "No people, no hands, no pets, no animated phone screens, no TVs/monitors with UI, "
        "no steam, no water, no text overlays, no sale tags, no price signs. "
        "Preserve exact product shape, color, branding, label text, materials, and packaging from the reference."
    )


def _upscale_to_1080x1920(image_bytes: bytes) -> bytes:
    from PIL import Image

    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    if img.size != (TARGET_WIDTH, TARGET_HEIGHT):
        img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    out = BytesIO()
    img.save(out, format="JPEG", quality=92)
    return out.getvalue()


def generate_module4_sample(
    *,
    product_name: str,
    source_image: Path,
    reference_image: Path | None = None,
    style: str = "auto",
    out_path: Path | None = None,
    force: bool = False,
) -> SampleImageResult:
    """Gemini image model → full-bleed 9:16 JPEG for Kling."""
    src = Path(source_image)
    if not src.is_file():
        raise FileNotFoundError(f"Source product image not found: {src}")

    dest = out_path or sample_image_path(product_name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and not force and dest.stat().st_size > 5000:
        from PIL import Image

        im = Image.open(dest)
        return SampleImageResult(
            product_name=product_name,
            source_image=str(src.resolve()),
            sample_path=dest,
            width=im.size[0],
            height=im.size[1],
            model="cached",
            prompt_used="",
        )

    from google.genai import types
    from PIL import Image

    client = _require_gemini_client()
    model = (settings.gemini_image_model or "gemini-2.5-flash-image").strip()
    prompt = build_sample_prompt(
        product_name=product_name,
        style=style,
        reference_note=reference_image is not None and Path(reference_image).is_file(),
    )

    contents: list = [prompt, Image.open(src)]
    if reference_image and Path(reference_image).is_file():
        contents.insert(1, Image.open(reference_image))

    resp = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="9:16"),
        ),
    )

    raw_bytes: bytes | None = None
    for part in resp.parts:
        if part.inline_data is not None:
            data = part.inline_data.data
            if isinstance(data, bytes):
                raw_bytes = data
            else:
                raw_bytes = bytes(data)
            break

    if not raw_bytes:
        text = getattr(resp, "text", "") or ""
        raise RuntimeError(f"Gemini returned no image for Module 4 sample. {text[:300]}")

    final = _upscale_to_1080x1920(raw_bytes)
    dest.write_bytes(final)

    im = Image.open(BytesIO(final))
    return SampleImageResult(
        product_name=product_name,
        source_image=str(src.resolve()),
        sample_path=dest,
        width=im.size[0],
        height=im.size[1],
        model=model,
        prompt_used=prompt,
    )
