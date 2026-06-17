"""Create Recraft custom style from reference images (API multipart upload)."""

from __future__ import annotations

import json
import mimetypes
import uuid
from pathlib import Path

import urllib.error
import urllib.request

RECRAFT_API_BASE = "https://external.api.recraft.ai/v1"


def create_recraft_style(
    image_paths: list[Path],
    *,
    api_key: str,
    base_style: str = "digital_illustration",
) -> str:
    """Upload up to 5 reference PNG/JPG/WEBP images; return style UUID."""
    paths = [p for p in image_paths if p.is_file()]
    if not paths:
        raise ValueError("No reference images found.")
    if len(paths) > 5:
        paths = paths[:5]

    total_bytes = sum(p.stat().st_size for p in paths)
    if total_bytes > 5 * 1024 * 1024:
        raise ValueError(
            f"Reference images total {total_bytes / 1024 / 1024:.1f} MB — Recraft limit is 5 MB."
        )

    boundary = f"----shortsbot{uuid.uuid4().hex}"
    body = bytearray()

    def add_field(name: str, value: str) -> None:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.extend(value.encode())
        body.extend(b"\r\n")

    add_field("style", base_style)

    for i, path in enumerate(paths, start=1):
        mime, _ = mimetypes.guess_type(str(path))
        mime = mime or "image/png"
        data = path.read_bytes()
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(
            f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'.encode()
        )
        body.extend(f"Content-Type: {mime}\r\n\r\n".encode())
        body.extend(data)
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode())

    req = urllib.request.Request(
        f"{RECRAFT_API_BASE}/styles",
        data=bytes(body),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "shorts-bot/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Recraft style API {exc.code}: {err[:500]}") from exc

    style_id = data.get("id") if isinstance(data, dict) else None
    if not style_id:
        raise RuntimeError(f"Recraft style response missing id: {data}")
    return str(style_id)
