"""Replicate FLUX image generation (pay-per-image)."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://api.replicate.com/v1"


def _request(method: str, url: str, *, token: str, payload: dict | None = None) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "shorts-bot/1.0",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Replicate API {exc.code}: {body[:400]}") from exc


def _poll_prediction(prediction_id: str, *, token: str, timeout_sec: int = 300) -> dict:
    url = f"{API_BASE}/predictions/{prediction_id}"
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        data = _request("GET", url, token=token)
        status = data.get("status")
        if status == "succeeded":
            return data
        if status in {"failed", "canceled"}:
            raise RuntimeError(f"Replicate prediction {status}: {data.get('error')}")
        time.sleep(2)
    raise TimeoutError(f"Replicate prediction {prediction_id} timed out")


def _download_url(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "shorts-bot/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def generate_replicate_image(
    prompt: str,
    out_path: Path,
    *,
    token: str,
    model: str = "black-forest-labs/flux-schnell",
    aspect_ratio: str = "9:16",
) -> str:
    """Run Replicate model and save first output image to out_path."""
    if "/" not in model:
        raise ValueError(f"Invalid Replicate model slug: {model}")

    owner, name = model.split("/", 1)
    url = f"{API_BASE}/models/{owner}/{name}/predictions"
    body = {
        "input": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "num_outputs": 1,
            "output_format": "png",
            "go_fast": True,
        }
    }
    created = _request("POST", url, token=token, payload=body)
    pred_id = created.get("id")
    if not pred_id:
        raise RuntimeError(f"Replicate returned no prediction id: {created}")

    result = _poll_prediction(pred_id, token=token)
    output = result.get("output")
    if not output:
        raise RuntimeError(f"Replicate empty output: {result}")

    image_url = output[0] if isinstance(output, list) else output
    if not isinstance(image_url, str):
        raise RuntimeError(f"Unexpected Replicate output type: {type(output)}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _download_url(image_url, out_path)
    return f"replicate/{model}"


def probe_replicate(token: str, model: str = "black-forest-labs/flux-schnell") -> tuple[bool, str]:
    try:
        owner, name = model.split("/", 1)
        url = f"{API_BASE}/models/{owner}/{name}"
        _request("GET", url, token=token)
        return True, f"Replicate model {model} reachable"
    except Exception as exc:
        return False, str(exc)[:200]
