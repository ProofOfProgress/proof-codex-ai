"""Replicate image generation helpers.

This module is kept for status checks and legacy image-pack paths. The main
daily channel production now runs through InVideo, but login/status should not
crash when a Replicate token is present in cloud secrets.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


API_BASE = "https://api.replicate.com/v1"


def _request_json(
    url: str,
    *,
    token: str,
    payload: dict[str, Any] | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "shorts-bot/1.0",
        },
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Replicate API {exc.code}: {body[:400]}") from exc


def _download_url(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "shorts-bot/1.0"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        dest.write_bytes(resp.read())


def _prediction_url(model: str) -> str:
    parts = [p for p in model.strip().split("/") if p]
    if len(parts) == 2:
        owner, name = parts
        return f"{API_BASE}/models/{owner}/{name}/predictions"
    return f"{API_BASE}/predictions"


def _prediction_payload(prompt: str, *, model: str, aspect_ratio: str) -> dict[str, Any]:
    input_payload: dict[str, Any] = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "output_format": "png",
    }
    payload: dict[str, Any] = {"input": input_payload}
    if len([p for p in model.strip().split("/") if p]) != 2:
        payload["version"] = model.strip()
    return payload


def _first_output_url(output: Any) -> str | None:
    if isinstance(output, str) and output.startswith("http"):
        return output
    if isinstance(output, list):
        for item in output:
            url = _first_output_url(item)
            if url:
                return url
    if isinstance(output, dict):
        for key in ("url", "image", "output"):
            url = _first_output_url(output.get(key))
            if url:
                return url
    return None


def generate_replicate_image(
    prompt: str,
    out_path: Path,
    *,
    token: str,
    model: str,
    aspect_ratio: str = "9:16",
) -> str:
    """Create one image with Replicate and save it to ``out_path``."""
    if not token.strip():
        raise ValueError("REPLICATE_API_TOKEN not set.")
    if not model.strip():
        raise ValueError("Replicate image model not set.")

    prediction = _request_json(
        _prediction_url(model),
        token=token,
        payload=_prediction_payload(prompt, model=model, aspect_ratio=aspect_ratio),
    )
    status = prediction.get("status")
    poll_url = (prediction.get("urls") or {}).get("get")
    deadline = time.time() + 240
    while status not in {"succeeded", "failed", "canceled"} and poll_url and time.time() < deadline:
        time.sleep(3)
        prediction = _request_json(poll_url, token=token, timeout=60)
        status = prediction.get("status")

    if status != "succeeded":
        err = prediction.get("error") or prediction
        raise RuntimeError(f"Replicate image generation did not succeed: {err}")

    image_url = _first_output_url(prediction.get("output"))
    if not image_url:
        raise RuntimeError(f"Replicate returned no image URL: {prediction}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _download_url(image_url, out_path)
    return f"replicate/{model}"


def probe_replicate(token: str, model: str) -> tuple[bool, str]:
    """Cheap token/model check for login-status and doctor output."""
    if not token.strip():
        return False, "REPLICATE_API_TOKEN missing"
    model = model.strip()
    if not model:
        return False, "Replicate image model missing"
    parts = [p for p in model.split("/") if p]
    if len(parts) != 2:
        return True, "Replicate token configured; version-style model will be checked at generation time"
    try:
        data = _request_json(f"{API_BASE}/models/{parts[0]}/{parts[1]}", token=token, timeout=30)
        owner = (data.get("owner") or parts[0]) if isinstance(data, dict) else parts[0]
        name = (data.get("name") or parts[1]) if isinstance(data, dict) else parts[1]
        return True, f"Replicate model reachable: {owner}/{name}"
    except RuntimeError as exc:
        text = str(exc)
        if "401" in text or "403" in text:
            return False, text[:200]
        if "404" in text:
            return False, f"Replicate model not found: {model}"
        return False, text[:200]
    except Exception as exc:
        return False, str(exc)[:200]
