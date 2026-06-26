"""Replicate FLUX / image model generation."""

from __future__ import annotations

import time
from pathlib import Path

import httpx


def generate_replicate_image(
    prompt: str,
    out_path: Path,
    *,
    token: str,
    model: str,
    aspect_ratio: str = "9:16",
    poll_sec: float = 2.0,
    timeout_sec: int = 180,
) -> str:
    """Run one Replicate prediction and save the first output image."""
    if "/" not in model:
        raise ValueError(f"Invalid replicate model slug: {model}")
    owner, name = model.split("/", 1)
    headers = {"Authorization": f"Bearer {token.strip()}", "Content-Type": "application/json"}
    create_url = f"https://api.replicate.com/v1/models/{owner}/{name}/predictions"
    body = {"input": {"prompt": prompt, "aspect_ratio": aspect_ratio, "num_outputs": 1}}

    with httpx.Client(timeout=60.0) as client:
        resp = client.post(create_url, headers=headers, json=body)
        if resp.status_code >= 400:
            raise RuntimeError(f"Replicate create failed ({resp.status_code}): {resp.text[:300]}")
        pred = resp.json()
        pred_id = pred.get("id")
        if not pred_id:
            raise RuntimeError(f"Replicate missing prediction id: {pred}")

        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            poll = client.get(
                f"https://api.replicate.com/v1/predictions/{pred_id}",
                headers=headers,
            )
            poll.raise_for_status()
            data = poll.json()
            status = (data.get("status") or "").lower()
            if status == "succeeded":
                output = data.get("output")
                url = output[0] if isinstance(output, list) else output
                if not url:
                    raise RuntimeError(f"Replicate succeeded but no output: {data}")
                img = client.get(str(url), follow_redirects=True)
                img.raise_for_status()
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(img.content)
                return f"replicate/{model}"
            if status in {"failed", "canceled"}:
                raise RuntimeError(f"Replicate {status}: {data.get('error') or data}")
            time.sleep(poll_sec)

    raise TimeoutError(f"Replicate prediction {pred_id} timed out")
