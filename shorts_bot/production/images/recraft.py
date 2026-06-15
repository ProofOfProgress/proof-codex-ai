"""Recraft API — crayon/illustration stills with custom style_id."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

RECRAFT_API_BASE = "https://external.api.recraft.ai/v1"


def _download_url(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "shorts-bot/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def _request(
    method: str,
    path: str,
    *,
    api_key: str,
    payload: dict | None = None,
    timeout: int = 180,
) -> dict:
    url = f"{RECRAFT_API_BASE}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "shorts-bot/1.0",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Recraft API {exc.code}: {err[:400]}") from exc


def generate_recraft_image(
    prompt: str,
    out_path: Path,
    *,
    api_key: str,
    model: str = "recraftv3",
    style_id: str | None = None,
    size: str = "1024x1820",
) -> str:
    """Generate one vertical still via Recraft and save to out_path."""
    payload: dict = {
        "prompt": prompt,
        "model": model,
        "size": size,
        "n": 1,
        "response_format": "url",
    }
    sid = (style_id or "").strip()
    if sid:
        payload["style_id"] = sid

    data = _request("POST", "/images/generations", api_key=api_key, payload=payload)
    items = data.get("data") or []
    if not items:
        raise RuntimeError(f"Recraft returned no images: {data}")

    item = items[0]
    image_url = item.get("url") if isinstance(item, dict) else None
    if not image_url:
        raise RuntimeError(f"Recraft image missing url: {item}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _download_url(image_url, out_path)
    tag = f"recraft/{model}"
    if sid:
        tag += f"/style={sid[:8]}"
    return tag


def probe_recraft(api_key: str) -> tuple[bool, str]:
    """Check API token and report remaining API units (credits)."""
    key = (api_key or "").strip()
    if not key:
        return False, "RECRAFT_API_KEY missing"
    try:
        data = _request("GET", "/users/me", api_key=key, timeout=30)
    except RuntimeError as exc:
        msg = str(exc)
        if "401" in msg or "403" in msg:
            return False, "Invalid Recraft API key"
        return False, msg[:200]

    credits = data.get("credits")
    email = data.get("email") or "account"
    if credits is None:
        return True, f"Recraft API key valid ({email})"
    try:
        balance = int(credits)
    except (TypeError, ValueError):
        return True, f"Recraft API key valid ({email})"
    if balance <= 0:
        return (
            False,
            f"API key works but 0 API units left — buy units in Profile → API "
            f"(~$1 per 1,000 units; ~40 units per image on V3)",
        )
    return True, f"Recraft OK — {balance:,} API units ({email})"
