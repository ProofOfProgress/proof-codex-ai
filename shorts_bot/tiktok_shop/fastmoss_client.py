"""FastMoss OpenAPI client — TikTok Shop product research."""

from __future__ import annotations

import time
from typing import Any

import httpx

from shorts_bot.config import settings

DEFAULT_API_BASE = "https://openapi.fastmoss.com"
_TOKEN_CACHE: dict[str, Any] = {"token": "", "expires_at": 0.0}


def configured() -> bool:
    cid = (settings.fastmoss_client_id or "").strip()
    secret = (settings.fastmoss_client_secret or "").strip()
    if not cid or not secret:
        return False
    lower = (cid + secret).lower()
    return "placeholder" not in lower and "your-" not in lower


def _api_base() -> str:
    return (settings.fastmoss_api_base or DEFAULT_API_BASE).rstrip("/")


def fetch_access_token(*, force: bool = False) -> str:
    """Exchange client_id + client_secret for access_token."""
    if not configured():
        raise RuntimeError("FastMoss not configured")
    now = time.time()
    if not force and _TOKEN_CACHE["token"] and _TOKEN_CACHE["expires_at"] > now + 60:
        return str(_TOKEN_CACHE["token"])

    path = (settings.fastmoss_token_path or "/oauth/token").strip()
    if not path.startswith("/"):
        path = f"/{path}"
    url = f"{_api_base()}{path}"
    payload = {
        "client_id": settings.fastmoss_client_id,
        "client_secret": settings.fastmoss_client_secret,
        "grant_type": "client_credentials",
    }
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(url, json=payload)
    try:
        body = resp.json()
    except Exception as exc:
        raise RuntimeError(f"FastMoss token non-JSON ({resp.status_code}): {resp.text[:200]}") from exc
    if resp.status_code >= 400:
        raise RuntimeError(
            f"FastMoss token error ({resp.status_code}): {body}. "
            "Apply free API trial: https://developers.fastmoss.com/free-trial.html"
        )
    token = str(body.get("access_token") or body.get("data", {}).get("access_token") or "")
    if not token:
        raise RuntimeError(f"FastMoss token response missing access_token: {body}")
    expires_in = int(body.get("expires_in") or body.get("data", {}).get("expires_in") or 3600)
    _TOKEN_CACHE["token"] = token
    _TOKEN_CACHE["expires_at"] = now + max(300, expires_in)
    return token


def ping() -> dict[str, Any]:
    """Verify credentials and token exchange."""
    if not configured():
        return {
            "ok": False,
            "error": "not_configured",
            "message": (
                "Set FASTMOSS_CLIENT_ID + FASTMOSS_CLIENT_SECRET — "
                "register at developers.fastmoss.com and apply free trial"
            ),
        }
    try:
        token = fetch_access_token()
    except RuntimeError as exc:
        return {"ok": False, "error": "token_failed", "message": str(exc)}
    return {
        "ok": False,
        "error": "scout_not_wired",
        "message": (
            "FastMoss token OK but product rank endpoints not wired in bot yet. "
            "Use Kalodata KaloPilot (KALODATA_PILOT_TOKEN) or hub FastMoss UI until Phase 2 ships."
        ),
        "token_prefix": token[:12] + "...",
    }


def _get(path: str, *, params: dict[str, Any] | None = None, token: str = "") -> dict[str, Any]:
    url = f"{_api_base()}{path}"
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with httpx.Client(timeout=60.0) as client:
        resp = client.get(url, params=params or {}, headers=headers)
    try:
        body = resp.json()
    except Exception as exc:
        raise RuntimeError(f"FastMoss non-JSON ({resp.status_code}): {resp.text[:200]}") from exc
    if resp.status_code >= 400:
        raise RuntimeError(f"FastMoss error ({resp.status_code}): {body}")
    return body if isinstance(body, dict) else {"data": body}
