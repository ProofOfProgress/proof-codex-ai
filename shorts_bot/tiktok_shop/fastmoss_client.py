"""FastMoss OpenAPI client — TikTok Shop product research (replaces EchoTik)."""

from __future__ import annotations

from typing import Any

import httpx

from shorts_bot.config import settings

DEFAULT_API_BASE = "https://openapi.fastmoss.com"


def configured() -> bool:
    cid = (settings.fastmoss_client_id or "").strip()
    secret = (settings.fastmoss_client_secret or "").strip()
    if not cid or not secret:
        return False
    lower = (cid + secret).lower()
    return "placeholder" not in lower and "your-" not in lower


def _api_base() -> str:
    return (settings.fastmoss_api_base or DEFAULT_API_BASE).rstrip("/")


def ping() -> dict[str, Any]:
    """
    Verify credentials. Full token + product endpoints wired in FASTMOSS_SCOUT_PLAN phase 2.
    """
    if not configured():
        return {
            "ok": False,
            "error": "not_configured",
            "message": "Set FASTMOSS_CLIENT_ID + FASTMOSS_CLIENT_SECRET — docs/FOR_OWNER_FASTMOSS_SETUP.md",
        }
    return {
        "ok": False,
        "error": "scout_not_wired",
        "message": (
            "FastMoss credentials present but automated scout not shipped yet. "
            "Launch path A: pick 8–10 products in FastMoss app and tell the agent. "
            "See docs/FASTMOSS_SCOUT_PLAN.md"
        ),
        "client_id_prefix": (settings.fastmoss_client_id or "")[:8] + "...",
    }


def fetch_access_token() -> str:
    """Exchange client_id + client_secret for access_token — endpoint TBD from FastMoss docs."""
    if not configured():
        raise RuntimeError("FastMoss not configured")
    raise RuntimeError(
        "FastMoss token exchange not wired yet — see docs/FASTMOSS_SCOUT_PLAN.md"
    )


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
