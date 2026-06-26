"""Replicate image generation (FLUX, Nano Banana Pro, etc.)."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path


def _download_url(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "shorts-bot/1.0"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        dest.write_bytes(resp.read())


def _aspect_dimensions(aspect_ratio: str) -> tuple[int, int]:
    mapping = {
        "9:16": (1080, 1920),
        "16:9": (1920, 1080),
        "1:1": (1080, 1080),
        "4:3": (1440, 1080),
        "3:4": (1080, 1440),
    }
    return mapping.get((aspect_ratio or "9:16").strip(), (1080, 1920))


def generate_replicate_image(
    prompt: str,
    out_path: Path,
    *,
    token: str,
    model: str,
    aspect_ratio: str = "9:16",
) -> str:
    """Run a Replicate image model and save the first output file."""
    tok = (token or "").strip()
    if not tok:
        raise ValueError("REPLICATE_API_TOKEN not set.")
    m = (model or "").strip()
    if not m:
        raise ValueError("REPLICATE_IMAGE_MODEL not set.")

    width, height = _aspect_dimensions(aspect_ratio)
    body = {
        "input": {
            "prompt": (prompt or "").strip(),
            "aspect_ratio": aspect_ratio,
            "width": width,
            "height": height,
        },
    }
    create_url = f"https://api.replicate.com/v1/models/{m}/predictions"
    req = urllib.request.Request(
        create_url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Token {tok}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            prediction = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Replicate create failed ({exc.code}): {err[:400]}") from exc

    pred_id = prediction.get("id")
    if not pred_id:
        raise RuntimeError(f"Replicate missing prediction id: {prediction}")

    status_url = f"https://api.replicate.com/v1/predictions/{pred_id}"
    deadline = time.time() + 300
    output_url = ""
    while time.time() < deadline:
        poll_req = urllib.request.Request(
            status_url,
            headers={"Authorization": f"Token {tok}"},
        )
        with urllib.request.urlopen(poll_req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        status = (data.get("status") or "").lower()
        if status == "succeeded":
            out = data.get("output")
            if isinstance(out, list) and out:
                output_url = str(out[0])
            elif isinstance(out, str):
                output_url = out
            break
        if status in {"failed", "canceled"}:
            raise RuntimeError(f"Replicate failed: {data.get('error') or data}")
        time.sleep(3)

    if not output_url:
        raise RuntimeError("Replicate timed out waiting for image output")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _download_url(output_url, out_path)
    return f"replicate/{m}"
