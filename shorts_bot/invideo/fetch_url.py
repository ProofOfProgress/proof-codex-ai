"""Fetch exported MP4 from a share link (Google Drive, Dropbox, direct URL)."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx

from shorts_bot.invideo.import_cli import import_mp4
from shorts_bot.invideo.script_pack import draft_pack_dir

_DRIVE_ID_RE = re.compile(r"/file/d/([a-zA-Z0-9_-]+)")
_DRIVE_OPEN_RE = re.compile(r"[?&]id=([a-zA-Z0-9_-]+)")


def normalize_download_url(url: str) -> str:
    u = url.strip()
    if "dropbox.com" in u:
        if "dl=0" in u:
            return u.replace("dl=0", "dl=1")
        if "dl=1" in u:
            return u
        return u + ("&" if "?" in u else "?") + "dl=1"
    if "drive.google.com" in u:
        m = _DRIVE_ID_RE.search(u) or _DRIVE_OPEN_RE.search(u)
        if m:
            return f"https://drive.google.com/uc?export=download&id={m.group(1)}"
    return u


def _drive_confirm_token(html: str) -> str | None:
    m = re.search(r"confirm=([0-9A-Za-z_]+)", html)
    return m.group(1) if m else None


def download_mp4_from_url(url: str, dest: Path, *, timeout_sec: int = 600) -> int:
    dest = dest.expanduser().resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    fetch_url = normalize_download_url(url)

    with httpx.Client(follow_redirects=True, timeout=timeout_sec) as client:
        resp = client.get(fetch_url)
        resp.raise_for_status()

        # Google Drive large-file confirmation page
        if "drive.google.com" in fetch_url and "text/html" in (resp.headers.get("content-type") or ""):
            token = _drive_confirm_token(resp.text)
            file_id = parse_qs(urlparse(fetch_url).query).get("id", [None])[0]
            if token and file_id:
                confirm_url = (
                    f"https://drive.google.com/uc?export=download&id={file_id}&confirm={token}"
                )
                resp = client.get(confirm_url)
                resp.raise_for_status()

        content_type = (resp.headers.get("content-type") or "").lower()
        if "text/html" in content_type and len(resp.content) < 500_000:
            raise RuntimeError(
                "Link returned a web page, not a video file. "
                "Use a direct download link or Google Drive → Share → Anyone with the link."
            )

        dest.write_bytes(resp.content)
        size = dest.stat().st_size
        if size < 50_000:
            raise RuntimeError(f"Download too small ({size} bytes) — link may be wrong or expired.")
        if dest.suffix.lower() != ".mp4":
            # Sniff MP4 magic (ftyp)
            if resp.content[4:8] != b"ftyp":
                raise RuntimeError("Download does not look like an MP4 file.")
        return size


def fetch_for_draft(draft_id: int, url: str, *, dest_name: str = "final_short.mp4") -> Path:
    pack = draft_pack_dir(draft_id)
    pack.mkdir(parents=True, exist_ok=True)
    tmp = pack / "_fetch_tmp.mp4"
    download_mp4_from_url(url, tmp)
    return import_mp4(draft_id, tmp)
