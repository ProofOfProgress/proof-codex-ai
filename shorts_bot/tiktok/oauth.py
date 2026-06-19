"""TikTok OAuth — token storage, refresh, auth URLs."""

from __future__ import annotations

import json
import urllib.parse
from pathlib import Path
from typing import Any

import httpx

from shorts_bot.config import settings

TIKTOK_AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
DEFAULT_SCOPES = ("user.info.basic", "video.publish")
OAUTH_REDIRECT_URI = "http://127.0.0.1:8091/"


def token_path() -> Path:
    return settings.tiktok_token_path


def _secret_real(value: str | None) -> bool:
    v = (value or "").strip()
    if not v:
        return False
    lower = v.lower()
    return not any(p in lower for p in ("your-", "placeholder", "paste-your"))


def client_key() -> str | None:
    key = (settings.tiktok_client_key or "").strip()
    return key if _secret_real(key) else None


def client_secret() -> str | None:
    sec = (settings.tiktok_client_secret or "").strip()
    return sec if _secret_real(sec) else None


def credentials_configured() -> bool:
    return bool(client_key() and client_secret())


def redirect_uri() -> str:
    return (settings.tiktok_redirect_uri or OAUTH_REDIRECT_URI).strip()


def requested_scopes() -> list[str]:
    raw = (settings.tiktok_oauth_scopes or ",".join(DEFAULT_SCOPES)).strip()
    return [s.strip() for s in raw.split(",") if s.strip()]


def load_token_data() -> dict[str, Any]:
    path = token_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save_token_data(data: dict[str, Any]) -> Path:
    path = token_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def token_exists() -> bool:
    data = load_token_data()
    return bool(data.get("access_token"))


def upload_ready() -> bool:
    if not credentials_configured() or not token_exists():
        return False
    scopes = (load_token_data().get("scope") or "").split(",")
    return any("video.publish" in s or "video.upload" in s for s in scopes)


def auth_status() -> dict[str, Any]:
    data = load_token_data()
    scopes = (data.get("scope") or "").split(",")
    return {
        "credentials_configured": credentials_configured(),
        "token_saved": token_exists(),
        "upload_ready": upload_ready(),
        "open_id": data.get("open_id"),
        "scopes": [s for s in scopes if s],
        "redirect_uri": redirect_uri(),
    }


def credentials_status_message() -> str:
    if not credentials_configured():
        return "TIKTOK_CLIENT_KEY + TIKTOK_CLIENT_SECRET missing — see docs/FOR_OWNER_TIKTOK_SETUP.md"
    if not token_exists():
        return "TikTok app keys OK — run OAuth connect next"
    if upload_ready():
        return "TikTok OAuth OK — video.publish or video.upload granted"
    return "Token saved but missing video.publish scope — re-run auth_cli connect"


def oauth_authorization_url(*, state: str = "shorts_bot") -> str:
    ck = client_key()
    if not ck:
        raise RuntimeError("TIKTOK_CLIENT_KEY not configured")
    params = {
        "client_key": ck,
        "scope": ",".join(requested_scopes()),
        "response_type": "code",
        "redirect_uri": redirect_uri(),
        "state": state,
    }
    return TIKTOK_AUTH_URL + "?" + urllib.parse.urlencode(params)


def _exchange_token(payload: dict[str, str]) -> dict[str, Any]:
    ck = client_key()
    sec = client_secret()
    if not ck or not sec:
        raise RuntimeError("TikTok client key/secret not configured")
    payload = {"client_key": ck, "client_secret": sec, **payload}
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            TIKTOK_TOKEN_URL,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    try:
        body = resp.json()
    except Exception as exc:
        raise RuntimeError(f"TikTok token response not JSON: {resp.text[:200]}") from exc
    if resp.status_code >= 400 or body.get("error"):
        err = body.get("error_description") or body.get("error") or body
        raise RuntimeError(f"TikTok token error: {err}")
    return body


def oauth_complete_code(code: str) -> dict[str, Any]:
    body = _exchange_token(
        {
            "code": code.strip(),
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri(),
        }
    )
    data = {
        "access_token": body.get("access_token"),
        "refresh_token": body.get("refresh_token"),
        "expires_in": body.get("expires_in"),
        "refresh_expires_in": body.get("refresh_expires_in"),
        "open_id": body.get("open_id"),
        "scope": body.get("scope"),
        "token_type": body.get("token_type", "Bearer"),
    }
    save_token_data(data)
    return {"ok": True, "message": f"TikTok token saved → {token_path()}", "scope": data.get("scope")}


def oauth_complete_redirect(url: str) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(url.strip())
    qs = urllib.parse.parse_qs(parsed.query)
    if "code" not in qs:
        return {"ok": False, "message": "No code= in redirect URL"}
    return oauth_complete_code(qs["code"][0])


def refresh_access_token() -> dict[str, Any]:
    data = load_token_data()
    refresh = (data.get("refresh_token") or "").strip()
    if not refresh:
        raise RuntimeError("No TikTok refresh_token — run auth_cli connect")
    body = _exchange_token({"grant_type": "refresh_token", "refresh_token": refresh})
    merged = {**data, **{k: body.get(k) for k in (
        "access_token", "refresh_token", "expires_in", "refresh_expires_in", "scope", "open_id"
    ) if body.get(k) is not None}}
    save_token_data(merged)
    return merged


def get_access_token(*, force_refresh: bool = False) -> str:
    if force_refresh:
        return refresh_access_token()["access_token"]
    data = load_token_data()
    token = (data.get("access_token") or "").strip()
    if not token:
        raise RuntimeError("TikTok not connected — python3 -m shorts_bot.tiktok.auth_cli connect")
    return token
