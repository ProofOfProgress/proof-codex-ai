"""Gemini image generation — Nano Banana Pro (Module 4)."""

from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image


def _aspect_to_image_config(aspect_ratio: str, image_size: str) -> types.ImageConfig:
    ar = (aspect_ratio or "9:16").strip()
    size = (image_size or "2K").strip().upper()
    if size not in {"1K", "2K", "4K"}:
        size = "2K"
    return types.ImageConfig(aspect_ratio=ar, image_size=size)


def _load_reference(path: Path) -> Image.Image:
    if not path.is_file():
        raise FileNotFoundError(path)
    return Image.open(path)


def _save_first_image(response: types.GenerateContentResponse, out_path: Path) -> None:
    candidates = response.candidates or []
    for candidate in candidates:
        content = candidate.content
        if not content or not content.parts:
            continue
        for part in content.parts:
            inline = part.inline_data
            if inline and inline.data:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                raw = inline.data
                if isinstance(raw, str):
                    raw = base64.b64decode(raw)
                img = Image.open(BytesIO(raw))
                img.save(out_path)
                return
            if hasattr(part, "as_image"):
                try:
                    img = part.as_image()
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    img.save(out_path)
                    return
                except Exception:
                    pass
    raise RuntimeError("Gemini returned no image bytes")


def generate_gemini_image(
    prompt: str,
    out_path: Path,
    *,
    api_key: str,
    model: str = "gemini-3-pro-image-preview",
    aspect_ratio: str = "9:16",
    image_size: str = "2K",
    reference_images: list[Path] | None = None,
) -> str:
    """Generate one image via Gemini (Nano Banana Pro / Flash Image)."""
    key = (api_key or "").strip()
    if not key:
        raise ValueError("GEMINI_API_KEY not set.")

    text = (prompt or "").strip()
    if not text:
        raise ValueError("Image prompt is empty.")

    client = genai.Client(api_key=key)
    contents: list[object] = [text]
    for ref in reference_images or []:
        contents.append(_load_reference(ref))

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=_aspect_to_image_config(aspect_ratio, image_size),
    )

    response = client.models.generate_content(
        model=(model or "gemini-3-pro-image-preview").strip(),
        contents=contents,
        config=config,
    )
    _save_first_image(response, out_path)
    return f"gemini/{model}"


def probe_gemini(api_key: str, model: str = "gemini-3-pro-image-preview") -> tuple[bool, str]:
    try:
        client = genai.Client(api_key=(api_key or "").strip())
        client.models.get(model=model)
        return True, f"Gemini image model reachable ({model})"
    except Exception as exc:
        return False, str(exc)[:200]
