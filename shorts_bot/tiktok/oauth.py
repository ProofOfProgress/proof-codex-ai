"""TikTok OAuth — token storage, refresh, auth URLs."""

from __future__ import annotations

import hashlib
import json
import secrets
import urllib.parse
from pathlib import Path
from typing import Any

import httpx

from shorts_bot.config import settings

TIKTOK_AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
DEFAULT_SCOPES = ("user.info.basic", "video.publish")
OAUTH_REDIRECT_URI = "http://127.0.0.1:8091/"
_PKCE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"


def generate_pkce_pair(*, length: int = 64) -> tuple[str, str]:
    """TikTok desktop PKCE — challenge is hex(SHA256(verifier)), not base64url."""
    verifier = "".join(secrets.choice(_PKCE_CHARS) for _ in range(length))
    challenge = hashlib.sha256(verifier.encode("utf-8")).hexdigest()
    return verifier, challenge


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


def load_token_data(path: Path | None = None) -> dict[str, Any]:
    path = path or token_path()
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


def token_exists(path: Path | None = None) -> bool:
    data = load_token_data(path)
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


def save_pending_pkce(code_verifier: str) -> Path:
    path = settings.data_dir / "tiktok_oauth_pending.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"code_verifier": code_verifier}), encoding="utf-8")
    return path


def load_pending_pkce() -> str | None:
    path = settings.data_dir / "tiktok_oauth_pending.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    verifier = (data.get("code_verifier") or "").strip()
    return verifier or None


def clear_pending_pkce() -> None:
    path = settings.data_dir / "tiktok_oauth_pending.json"
    if path.exists():
        path.unlink(missing_ok=True)


def oauth_authorization_url_with_pkce(*, state: str = "shorts_bot") -> tuple[str, str]:
    verifier, challenge = generate_pkce_pair()
    url = oauth_authorization_url(state=state, code_challenge=challenge)
    save_pending_pkce(verifier)
    return url, verifier


def oauth_authorization_url(
    *,
    state: str = "shorts_bot",
    code_challenge: str | None = None,
    code_challenge_method: str = "S256",
) -> str:
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
    if code_challenge:
        params["code_challenge"] = code_challenge
        params["code_challenge_method"] = code_challenge_method
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


def oauth_complete_code(code: str, *, code_verifier: str | None = None) -> dict[str, Any]:
    payload: dict[str, str] = {
        "code": code.strip(),
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri(),
    }
    if code_verifier:
        payload["code_verifier"] = code_verifier.strip()
    body = _exchange_token(payload)
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


def oauth_complete_redirect(url: str, *, code_verifier: str | None = None) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(url.strip())
    qs = urllib.parse.parse_qs(parsed.query)
    if "code" not in qs:
        return {"ok": False, "message": "No code= in redirect URL"}
    return oauth_complete_code(qs["code"][0], code_verifier=code_verifier)


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


def get_access_token(*, force_refresh: bool = False, path: Path | None = None) -> str:
    if force_refresh:
        return refresh_access_token()["access_token"]
    data = load_token_data(path)
    token = (data.get("access_token") or "").strip()
    if not token:
        label = path or token_path()
        raise RuntimeError(f"TikTok not connected — token missing at {label}")
    return token


def run_oauth_flow(
    *,
    open_browser: bool = True,
    timeout_sec: int = 300,
    auth_url: str | None = None,
) -> dict[str, Any]:
    """
    Start localhost callback on :8091, open TikTok authorize URL, save token on redirect.
    Works on Cloud VM Desktop browser — user logs in and taps Allow.
    """
    import threading
    import webbrowser
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import parse_qs, urlparse

    if not credentials_configured():
        return {"ok": False, "message": credentials_status_message()}

    code_verifier = load_pending_pkce()
    if code_verifier:
        code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).hexdigest()
        if not auth_url:
            auth_url = oauth_authorization_url(code_challenge=code_challenge)
    else:
        code_verifier, code_challenge = generate_pkce_pair()
        save_pending_pkce(code_verifier)
        auth_url = auth_url or oauth_authorization_url(code_challenge=code_challenge)
    captured: dict[str, str | None] = {"code": None, "error": None}
    server_ref: list[HTTPServer] = []

    class _OAuthHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            qs = parse_qs(urlparse(self.path).query)
            if qs.get("code"):
                captured["code"] = qs["code"][0]
                body = b"<html><body><h1>TikTok connected</h1><p>Close this tab.</p></body></html>"
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif qs.get("error"):
                captured["error"] = qs.get("error_description", qs.get("error", ["unknown"]))[0]
                self.send_response(400)
                self.end_headers()
            else:
                self.send_response(400)
                self.end_headers()
            if server_ref:
                threading.Thread(target=server_ref[0].shutdown, daemon=True).start()

        def log_message(self, *_args: object) -> None:
            return

    port = 8091
    uri = redirect_uri()
    if uri.startswith("http://127.0.0.1:"):
        try:
            port = int(uri.split(":")[2].split("/")[0])
        except (IndexError, ValueError):
            port = 8091

    server = HTTPServer(("127.0.0.1", port), _OAuthHandler)
    server_ref.append(server)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    auth_url = auth_url or oauth_authorization_url(code_challenge=code_challenge)
    if open_browser:
        try:
            webbrowser.open(auth_url)
        except Exception:
            pass
        try:
            from shorts_bot.browser.session import spawn_visible_browser

            spawn_visible_browser(auth_url, minutes=max(5, timeout_sec // 60))
        except Exception:
            pass

    thread.join(timeout=timeout_sec)
    server.shutdown()

    if captured["error"]:
        return {"ok": False, "message": f"TikTok OAuth denied: {captured['error']}"}
    if not captured["code"]:
        return {
            "ok": False,
            "message": (
                "No OAuth code received — log into TikTok in the browser, tap Allow, "
                "or paste redirect URL: python3 -m shorts_bot.tiktok.auth_cli url --complete 'URL'"
            ),
            "auth_url": auth_url,
        }
    result = oauth_complete_code(captured["code"], code_verifier=code_verifier)
    if result.get("ok"):
        clear_pending_pkce()
    return result
