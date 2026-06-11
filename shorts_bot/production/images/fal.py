"""Fal.ai FLUX image generation (pay-per-image)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path


def _download_url(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "shorts-bot/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def generate_fal_image(
    prompt: str,
    out_path: Path,
    *,
    api_key: str,
    model: str = "fal-ai/flux/schnell",
) -> str:
    """Call Fal.ai sync endpoint and save image."""
    url = f"https://fal.run/{model}"
    payload = {
        "prompt": prompt,
        "image_size": {"width": 1080, "height": 1920},
        "num_images": 1,
        "enable_safety_checker": True,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Fal API {exc.code}: {err[:400]}") from exc

    images = data.get("images") or []
    if not images:
        raise RuntimeError(f"Fal returned no images: {data}")

    image_url = images[0].get("url") if isinstance(images[0], dict) else images[0]
    if not image_url:
        raise RuntimeError(f"Fal image missing url: {images[0]}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _download_url(image_url, out_path)
    return f"fal/{model}"


def probe_fal(api_key: str) -> tuple[bool, str]:
    try:
        url = "https://fal.run/fal-ai/flux/schnell"
        req = urllib.request.Request(
            url,
            data=json.dumps({"prompt": "test", "num_images": 0}).encode(),
            headers={"Authorization": f"Key {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30):
            pass
        return True, "Fal API key accepted"
    except urllib.error.HTTPError as exc:
        if exc.code in {400, 422}:
            return True, "Fal API key valid (dry probe)"
        body = exc.read().decode("utf-8", errors="replace")
        return False, f"Fal {exc.code}: {body[:120]}"
    except Exception as exc:
        return False, str(exc)[:200]
