"""Google Drive API — list and download MP4s from an inbox folder."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.youtube.google_auth import drive_ready, load_credentials_for_drive

_FOLDER_ID_RE = re.compile(r"/folders/([a-zA-Z0-9_-]+)")
_FOLDER_OPEN_RE = re.compile(r"[?&]id=([a-zA-Z0-9_-]+)")


@dataclass(frozen=True)
class DriveFile:
    file_id: str
    name: str
    created_time: str
    size: int | None


def parse_folder_id(value: str) -> str:
    """Accept raw folder ID or a drive.google.com/drive/folders/… URL."""
    v = (value or "").strip()
    if not v:
        raise ValueError("Empty folder ID or URL")
    if "drive.google.com" in v:
        m = _FOLDER_ID_RE.search(v) or _FOLDER_OPEN_RE.search(v)
        if not m:
            raise ValueError("Could not parse folder ID from Drive URL")
        return m.group(1)
    return v


def drive_configured() -> bool:
    from shorts_bot.config import settings

    return bool(settings.google_drive_folder_id and settings.google_drive_inbox_enabled)


def drive_status_message() -> str:
    from shorts_bot.config import settings

    if not settings.google_drive_inbox_enabled:
        return "Drive inbox disabled (GOOGLE_DRIVE_INBOX_ENABLED=false)"
    if not settings.google_drive_folder_id:
        return "Set GOOGLE_DRIVE_FOLDER_ID — see docs/FOR_OWNER_DRIVE_SETUP.md"
    if not drive_ready():
        return (
            "Google token missing Drive scope — run: "
            "python3 -m shorts_bot.youtube.auth_cli connect"
        )
    return f"Inbox folder OK ({settings.google_drive_folder_id[:12]}…)"


def _drive_service():
    creds = load_credentials_for_drive()
    if not creds:
        raise RuntimeError(drive_status_message())
    from googleapiclient.discovery import build

    return build("drive", "v3", credentials=creds, cache_discovery=False)


def list_mp4s(folder_id: str, *, limit: int = 20) -> list[DriveFile]:
    folder_id = parse_folder_id(folder_id)
    service = _drive_service()
    query = (
        f"'{folder_id}' in parents and trashed=false and "
        "(mimeType='video/mp4' or name contains '.mp4')"
    )
    resp = (
        service.files()
        .list(
            q=query,
            orderBy="createdTime desc",
            pageSize=limit,
            fields="files(id,name,createdTime,size,mimeType)",
        )
        .execute()
    )
    out: list[DriveFile] = []
    for item in resp.get("files") or []:
        name = str(item.get("name") or "")
        if not name.lower().endswith(".mp4"):
            continue
        size_raw = item.get("size")
        size = int(size_raw) if size_raw is not None else None
        out.append(
            DriveFile(
                file_id=str(item["id"]),
                name=name,
                created_time=str(item.get("createdTime") or ""),
                size=size,
            )
        )
    return out


def find_folder_by_name(name: str) -> str | None:
    """Return folder ID if a folder with this exact name exists in My Drive."""
    service = _drive_service()
    safe_name = name.replace("'", "\\'")
    query = (
        f"mimeType='application/vnd.google-apps.folder' and trashed=false and "
        f"name='{safe_name}'"
    )
    resp = (
        service.files()
        .list(q=query, pageSize=5, fields="files(id,name)", orderBy="createdTime desc")
        .execute()
    )
    files = resp.get("files") or []
    return str(files[0]["id"]) if files else None


def create_folder(name: str, *, parent_id: str = "root") -> str:
    service = _drive_service()
    meta = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    created = service.files().create(body=meta, fields="id").execute()
    return str(created["id"])


def ensure_inbox_folder(name: str = "Rapid Tool Review Inbox") -> str:
    """Find or create the inbox folder; return folder ID."""
    existing = find_folder_by_name(name)
    if existing:
        return existing
    return create_folder(name)


def download_file(file_id: str, dest: Path) -> int:
    dest = dest.expanduser().resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    service = _drive_service()
    from googleapiclient.http import MediaIoBaseDownload

    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    data = buffer.getvalue()
    if len(data) < 50_000:
        raise RuntimeError(f"Download too small ({len(data)} bytes) — not a valid MP4")
    if len(data) >= 12 and data[4:8] != b"ftyp":
        raise RuntimeError("Download does not look like an MP4 file")
    dest.write_bytes(data)
    return len(data)
