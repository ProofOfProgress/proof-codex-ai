"""Replicate image generation and health checks."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


API_ROOT = "https://api.replicate.com/v1"


def _request(
    url: str,
    *,
    token: str,
    data: dict[str, Any] | None = None,
    method: str | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    body = json.dumps(data).encode("utf-8") if data is not None else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "shorts-bot/1.0",
    }
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw) if raw else {}


def _download_url(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "shorts-bot/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def _model_parts(model: str) -> tuple[str, str]:
    base = model.split(":", 1)[0].strip().strip("/")
    try:
        owner, name = base.split("/", 1)
    except ValueError as exc:
        raise ValueError(
            "Replicate image model must look like 'owner/model' or 'owner/model:version'."
        ) from exc
    return owner, name


def _prediction_output_url(output: Any) -> str | None:
    if isinstance(output, str):
        return output
    if isinstance(output, list) and output:
        first = output[0]
        if isinstance(first, str):
            return first
        if isinstance(first, dict):
            return first.get("url")
    if isinstance(output, dict):
        return output.get("url")
    return None


def generate_replicate_image(
    prompt: str,
    out_path: Path,
    *,
    token: str,
    model: str,
    aspect_ratio: str = "9:16",
) -> str:
    """Call Replicate's model prediction API and save the first image output."""
    owner, name = _model_parts(model)
    input_payload: dict[str, Any] = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "output_format": "png",
    }
    model_ref, sep, version = model.partition(":")
    if sep and version.strip():
        create_url = f"{API_ROOT}/predictions"
        payload = {"version": version.strip(), "input": input_payload}
    else:
        create_url = f"{API_ROOT}/models/{owner}/{name}/predictions"
        payload = {"input": input_payload}

    try:
        prediction = _request(create_url, token=token, data=payload, method="POST", timeout=90)
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Replicate API {exc.code}: {err[:400]}") from exc

    get_url = prediction.get("urls", {}).get("get")
    if not get_url:
        raise RuntimeError(f"Replicate prediction missing poll URL: {prediction}")

    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        status = str(prediction.get("status") or "").lower()
        if status == "succeeded":
            image_url = _prediction_output_url(prediction.get("output"))
            if not image_url:
                raise RuntimeError(f"Replicate returned no image URL: {prediction}")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            _download_url(image_url, out_path)
            return f"replicate/{model_ref.strip()}"
        if status in {"failed", "canceled"}:
            raise RuntimeError(f"Replicate prediction {status}: {prediction.get('error')}")
        time.sleep(3)
        prediction = _request(get_url, token=token, timeout=60)

    raise TimeoutError("Replicate image generation timed out after 600 seconds.")


def probe_replicate(token: str, model: str) -> tuple[bool, str]:
    """Validate the token and configured image model without generating media."""
    try:
        owner, name = _model_parts(model)
        _request(f"{API_ROOT}/models/{owner}/{name}", token=token, timeout=30)
        return True, f"Replicate API key accepted for {owner}/{name}"
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 401:
            return False, "Replicate 401: API token rejected"
        if exc.code == 404:
            return False, f"Replicate model not found: {model}"
        return False, f"Replicate {exc.code}: {body[:120]}"
    except Exception as exc:
        return False, str(exc)[:200]
