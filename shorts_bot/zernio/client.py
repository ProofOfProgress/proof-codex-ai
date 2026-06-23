"""Zernio REST client — accounts, media presign, posts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from shorts_bot.config import settings

API_BASE = "https://zernio.com/api/v1"


def api_key() -> str | None:
    key = (settings.zernio_api_key or "").strip()
    if not key or "your-" in key.lower() or key.startswith("sk_your"):
        return None
    return key


def credentials_configured() -> bool:
    return bool(api_key())


def _headers() -> dict[str, str]:
    key = api_key()
    if not key:
        raise RuntimeError("ZERNIO_API_KEY missing — add to Cursor Secrets or .env")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def _request(method: str, path: str, *, json: dict[str, Any] | None = None) -> dict[str, Any]:
    with httpx.Client(timeout=120.0) as client:
        resp = client.request(method, f"{API_BASE}{path}", headers=_headers(), json=json)
    try:
        body = resp.json()
    except Exception as exc:
        raise RuntimeError(f"Zernio non-JSON ({resp.status_code}): {resp.text[:300]}") from exc
    if resp.status_code >= 400:
        err = body.get("error") or body.get("message") or body
        raise RuntimeError(f"Zernio API {resp.status_code}: {err}")
    return body if isinstance(body, dict) else {"data": body}


def list_accounts() -> list[dict[str, Any]]:
    body = _request("GET", "/accounts")
    accounts = body.get("accounts") or body.get("data") or []
    return accounts if isinstance(accounts, list) else []


def account_id_for(platform: str) -> str | None:
    """Resolve Zernio account id — env override, else first active match."""
    platform = platform.strip().lower()
    overrides = {
        "tiktok": (settings.zernio_tiktok_account_id or "").strip(),
        "facebook": (settings.zernio_facebook_account_id or "").strip(),
    }
    if overrides.get(platform):
        return overrides[platform]
    for acct in list_accounts():
        if (acct.get("platform") or "").lower() != platform:
            continue
        if acct.get("isActive") is False or acct.get("enabled") is False:
            continue
        aid = (acct.get("_id") or acct.get("id") or "").strip()
        if aid:
            return aid
    return None


def presign_video(video_path: Path) -> tuple[str, str]:
    """Return (upload_url, public_url) for an MP4."""
    size = video_path.stat().st_size
    body = _request(
        "POST",
        "/media/presign",
        json={
            "filename": video_path.name,
            "contentType": "video/mp4",
            "size": size,
        },
    )
    upload_url = body.get("uploadUrl") or body.get("upload_url")
    public_url = body.get("publicUrl") or body.get("public_url")
    if not upload_url or not public_url:
        raise RuntimeError(f"Zernio presign missing URLs: {body}")
    return str(upload_url), str(public_url)


def upload_file_to_presigned(upload_url: str, video_path: Path) -> None:
    raw = video_path.read_bytes()
    with httpx.Client(timeout=600.0) as client:
        resp = client.put(
            upload_url,
            content=raw,
            headers={"Content-Type": "video/mp4", "Content-Length": str(len(raw))},
        )
    if resp.status_code not in (200, 201, 204):
        raise RuntimeError(f"Zernio media upload failed ({resp.status_code}): {resp.text[:300]}")
