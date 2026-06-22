"""Replicate image generation adapter."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def _api_request(
    url: str,
    *,
    token: str,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: int = 60,
) -> Any:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "shorts-bot/1.0",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw) if raw else {}


def _download_url(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "shorts-bot/1.0"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        dest.write_bytes(resp.read())


def _first_image_url(output: Any) -> str | None:
    if isinstance(output, str) and output.startswith("http"):
        return output
    if isinstance(output, list):
        for item in output:
            found = _first_image_url(item)
            if found:
                return found
    if isinstance(output, dict):
        for key in ("url", "image", "output"):
            found = _first_image_url(output.get(key))
            if found:
                return found
    return None


def generate_replicate_image(
    prompt: str,
    out_path: Path,
    *,
    token: str,
    model: str,
    aspect_ratio: str = "9:16",
) -> str:
    """Call Replicate predictions API and save the first returned image."""
    payload = {
        "input": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "output_format": out_path.suffix.lstrip(".") or "png",
        }
    }
    try:
        data = _api_request(
            f"https://api.replicate.com/v1/models/{model}/predictions",
            token=token,
            method="POST",
            payload=payload,
            timeout=180,
        )
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Replicate API {exc.code}: {body[:400]}") from exc

    output_url = _first_image_url(data.get("output"))
    if not output_url:
        urls = data.get("urls") if isinstance(data, dict) else None
        get_url = urls.get("get") if isinstance(urls, dict) else None
        if get_url:
            # Poll a few times for async models; most image models finish quickly.
            import time

            for _ in range(30):
                time.sleep(2)
                polled = _api_request(get_url, token=token, timeout=30)
                status = str(polled.get("status") or "").lower()
                output_url = _first_image_url(polled.get("output"))
                if output_url:
                    break
                if status in {"failed", "canceled"}:
                    raise RuntimeError(f"Replicate prediction {status}: {polled.get('error')}")

    if not output_url:
        raise RuntimeError(f"Replicate returned no image output: {data}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _download_url(output_url, out_path)
    return f"replicate/{model}"


def probe_replicate(token: str, model: str) -> tuple[bool, str]:
    """Validate token/model reachability without creating an image."""
    try:
        _api_request(f"https://api.replicate.com/v1/models/{model}", token=token, timeout=30)
        return True, "Replicate API key accepted"
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 404:
            return False, f"Replicate model not found: {model}"
        if exc.code in {401, 403}:
            return False, f"Replicate token rejected ({exc.code})"
        return False, f"Replicate {exc.code}: {body[:120]}"
    except Exception as exc:
        return False, str(exc)[:200]
