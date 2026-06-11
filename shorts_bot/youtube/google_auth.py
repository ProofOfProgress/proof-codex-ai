from __future__ import annotations

import json
import os
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


def token_path() -> Path:
    return settings.youtube_token_path


def credentials_configured() -> bool:
    return bool(settings.google_client_id and settings.google_client_secret)


def token_exists() -> bool:
    return token_path().exists()


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


def run_oauth_flow() -> dict:
    """One-time OAuth in browser. User runs at home."""
    if not credentials_configured():
        return {
            "ok": False,
            "message": "Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env (Google Cloud Console).",
        }
    from google_auth_oauthlib.flow import InstalledAppFlow

    client_config = {
        "installed": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8090/"],
        }
    }
    # Always request upload + manage scopes so API upload works without Studio browser.
    oauth_scopes = UPLOAD_SCOPES
    flow = InstalledAppFlow.from_client_config(client_config, oauth_scopes)
    open_browser = os.environ.get("OAUTH_NO_BROWSER", "").lower() not in ("1", "true", "yes")
    last_err: Exception | None = None
    creds = None
    for port in (8090, 8091, 8092, 8093):
        try:
            creds = flow.run_local_server(
                port=port,
                open_browser=open_browser,
                prompt="consent",
            )
            break
        except OSError as exc:
            if getattr(exc, "errno", None) == 98:
                last_err = exc
                continue
            raise
    if creds is None:
        raise last_err or RuntimeError("Could not bind OAuth callback port.")
    save_credentials(creds, scopes=oauth_scopes)
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
        "token_saved": token_exists(),
        "ready": creds_ok,
        "upload_ready": upload_ok,
        "needs_upload_reauth": token_exists() and credentials_configured() and not upload_ok,
    }
