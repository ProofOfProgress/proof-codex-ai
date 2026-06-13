from __future__ import annotations

import json
import os
import pickle
from pathlib import Path

from shorts_bot.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
]

UPLOAD_SCOPES = SCOPES + [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",  # delete own videos
]

OAUTH_REDIRECT_URI = "http://127.0.0.1:8090/"
OAUTH_FLOW_PICKLE = Path("data/oauth_flow.pickle")

_PLACEHOLDER_FRAGMENTS = (
    "your-client-id",
    "your-client-secret",
    "your-key",
    "paste-your",
    "placeholder",
)


def token_path() -> Path:
    return settings.youtube_token_path


def _secret_real(value: str | None) -> bool:
    v = (value or "").strip()
    if not v:
        return False
    lower = v.lower()
    return not any(p in lower for p in _PLACEHOLDER_FRAGMENTS)


def credentials_configured() -> bool:
    return _secret_real(settings.google_client_id) and _secret_real(settings.google_client_secret)


def credentials_status_message() -> str:
    """Plain-English hint for login_status / auth_cli."""
    cid_env = os.environ.get("GOOGLE_CLIENT_ID")
    sec_env = os.environ.get("GOOGLE_CLIENT_SECRET")
    cid_file = (settings.google_client_id or "").strip()
    sec_file = (settings.google_client_secret or "").strip()

    if credentials_configured():
        return "Google OAuth app keys OK"

    if _secret_real(cid_env) and _secret_real(sec_env):
        return "Keys in environment but not .env — run: bash scripts/install.sh"

    if (_secret_real(cid_file) or _secret_real(sec_file)) and not (_secret_real(cid_env) and _secret_real(sec_env)):
        return "Keys look set in .env"

    if (cid_file or sec_file) and not credentials_configured():
        return (
            "GOOGLE_CLIENT_ID/SECRET still placeholder in .env — add them to "
            "Cursor → Cloud Agent → Secrets (not only IDE secrets), then bash scripts/install.sh"
        )
    return (
        "GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET missing on this VM — "
        "Cursor → Cloud Agent → Secrets → add both → bash scripts/install.sh"
    )


def token_exists() -> bool:
    return token_path().exists()


def import_token_json(raw: str) -> dict:
    """Save token from JSON string (YOUTUBE_TOKEN_JSON secret or home PC file)."""
    data = json.loads(raw)
    if not isinstance(data, dict) or "token" not in data and "refresh_token" not in data:
        raise ValueError("Invalid YouTube token JSON — need OAuth token file from auth_cli")
    path = token_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"ok": True, "message": f"YouTube token saved → {path}"}


def _client_config() -> dict:
    return {
        "installed": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [OAUTH_REDIRECT_URI, "http://localhost:8090/"],
        }
    }


def _make_flow():
    from google_auth_oauthlib.flow import InstalledAppFlow

    if not credentials_configured():
        raise RuntimeError(credentials_status_message())
    return InstalledAppFlow.from_client_config(_client_config(), UPLOAD_SCOPES)


def oauth_authorization_url() -> str:
    """
    Start OAuth on a trusted device (phone / home PC).
    Completes with oauth_complete_redirect() using the full localhost redirect URL.
    """
    flow = _make_flow()
    flow.redirect_uri = OAUTH_REDIRECT_URI
    auth_url, _state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    OAUTH_FLOW_PICKLE.parent.mkdir(parents=True, exist_ok=True)
    OAUTH_FLOW_PICKLE.write_bytes(pickle.dumps(flow))
    return auth_url


def oauth_complete_redirect(authorization_response: str) -> dict:
    """Paste full redirect URL after Google sign-in (http://127.0.0.1:8090/?code=...)."""
    if not OAUTH_FLOW_PICKLE.exists():
        return {
            "ok": False,
            "message": "No pending OAuth — run: python3 -m shorts_bot.youtube.auth_cli url",
        }
    flow = pickle.loads(OAUTH_FLOW_PICKLE.read_bytes())
    try:
        flow.fetch_token(authorization_response=authorization_response.strip())
    except Exception as exc:
        return {"ok": False, "message": f"OAuth failed: {exc}"}
    finally:
        try:
            OAUTH_FLOW_PICKLE.unlink(missing_ok=True)
        except OSError:
            pass
    save_credentials(flow.credentials, scopes=UPLOAD_SCOPES)
    return {
        "ok": True,
        "message": "YouTube connected with Analytics + API upload scopes. Token saved.",
    }


def _load_credentials(scopes: list[str]):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    path = token_path()
    if not path.exists():
        return None
    creds = Credentials.from_authorized_user_file(str(path), scopes)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_credentials(creds, scopes=scopes)
    return creds


def load_credentials():
    return _load_credentials(SCOPES)


def load_credentials_for_upload():
    """Load creds with upload scope; re-auth if token lacks youtube.upload."""
    creds = _load_credentials(UPLOAD_SCOPES)
    if not creds:
        return None
    granted = set(creds.scopes or [])
    if "https://www.googleapis.com/auth/youtube.upload" not in granted:
        return None
    return creds


def load_credentials_for_manage():
    """Upload + delete — needs youtube.force-ssl on token."""
    creds = _load_credentials(UPLOAD_SCOPES)
    if not creds:
        return None
    granted = set(creds.scopes or [])
    if "https://www.googleapis.com/auth/youtube.force-ssl" not in granted:
        return None
    return creds


def save_credentials(creds, *, scopes: list[str] | None = None) -> None:
    path = token_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(creds.to_json(), encoding="utf-8")


def run_oauth_flow(*, open_browser: bool | None = None) -> dict:
    """
    OAuth via localhost callback — uses your Desktop/system browser, NOT Playwright.
    Preferred on Cloud VM: click Desktop tab when browser opens.
    """
    if not credentials_configured():
        return {"ok": False, "message": credentials_status_message()}

    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_config(_client_config(), UPLOAD_SCOPES)
    if open_browser is None:
        open_browser = os.environ.get("OAUTH_NO_BROWSER", "").lower() not in ("1", "true", "yes")

    last_err: Exception | None = None
    creds = None
    for port in (8090, 8091, 8092, 8093):
        try:
            creds = flow.run_local_server(
                port=port,
                open_browser=open_browser,
                prompt="consent",
                authorization_prompt_message=(
                    "Open this URL in Chrome (Desktop tab or your phone if forwarded):\n{url}"
                ),
                success_message="YouTube connected — you can close this browser tab.",
            )
            break
        except OSError as exc:
            if getattr(exc, "errno", None) == 98:
                last_err = exc
                continue
            raise
    if creds is None:
        raise last_err or RuntimeError("Could not bind OAuth callback port.")
    save_credentials(creds, scopes=UPLOAD_SCOPES)
    return {
        "ok": True,
        "message": "YouTube connected with Analytics + API upload scopes. Token saved.",
    }


def upload_ready() -> bool:
    return load_credentials_for_upload() is not None


def auth_status() -> dict:
    creds_ok = credentials_configured() and token_exists()
    upload_ok = upload_ready()
    return {
        "credentials_configured": credentials_configured(),
        "credentials_message": credentials_status_message(),
        "token_saved": token_exists(),
        "ready": creds_ok,
        "upload_ready": upload_ok,
        "needs_upload_reauth": token_exists() and credentials_configured() and not upload_ok,
    }
