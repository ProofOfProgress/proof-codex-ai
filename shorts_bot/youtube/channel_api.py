"""Update channel name, description, and banner via YouTube Data API (no browser)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shorts_bot.youtube.google_auth import load_credentials_for_manage, load_credentials_for_upload


@dataclass
class ChannelApiResult:
    ok: bool
    message: str
    channel_id: str | None = None
    name_updated: bool = False
    description_updated: bool = False
    banner_updated: bool = False


def _youtube():
    from googleapiclient.discovery import build

    creds = load_credentials_for_manage() or load_credentials_for_upload()
    if not creds:
        raise RuntimeError(
            "YouTube OAuth required. Run: "
            "YOUTUBE_OAUTH_UPLOAD=1 python3 -m shorts_bot.youtube.auth_cli"
        )
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def get_my_channel_id() -> str:
    yt = _youtube()
    resp = yt.channels().list(part="id", mine=True).execute()
    items = resp.get("items") or []
    if not items:
        raise RuntimeError("No YouTube channel on this Google account.")
    return items[0]["id"]


def update_channel_text(
    *,
    channel_name: str | None = None,
    description: str | None = None,
) -> ChannelApiResult:
    """Set display name + description through brandingSettings.channel."""
    yt = _youtube()
    cid = get_my_channel_id()
    current = yt.channels().list(part="brandingSettings", id=cid).execute()
    items = current.get("items") or []
    branding = (items[0].get("brandingSettings") if items else {}) or {}
    channel_block = dict(branding.get("channel") or {})

    name_ok = False
    desc_ok = False
    if channel_name:
        channel_block["title"] = channel_name[:100]
        name_ok = True
    if description:
        channel_block["description"] = description[:1000]
        desc_ok = True

    if not name_ok and not desc_ok:
        return ChannelApiResult(False, "Nothing to update.")

    yt.channels().update(
        part="brandingSettings",
        body={"id": cid, "brandingSettings": {"channel": channel_block}},
    ).execute()

    parts = []
    if name_ok:
        parts.append("name")
    if desc_ok:
        parts.append("description")
    return ChannelApiResult(
        ok=True,
        message=f"Channel {' + '.join(parts)} updated via API.",
        channel_id=cid,
        name_updated=name_ok,
        description_updated=desc_ok,
    )


def upload_channel_banner(banner_path: Path) -> ChannelApiResult:
    """Upload banner image (2560×1440 recommended)."""
    if not banner_path.exists():
        return ChannelApiResult(False, f"Banner not found: {banner_path}")

    from googleapiclient.http import MediaFileUpload

    yt = _youtube()
    cid = get_my_channel_id()
    media = MediaFileUpload(str(banner_path), mimetype="image/png", resumable=True)
    yt.channelBanners().insert(channelId=cid, media_body=media).execute()
    return ChannelApiResult(
        ok=True,
        message=f"Banner uploaded from {banner_path.name}.",
        channel_id=cid,
        banner_updated=True,
    )


def apply_brand_from_files(
    *,
    channel_name: str | None = None,
    description: str | None = None,
    banner_path: Path | None = None,
) -> ChannelApiResult:
    """API-only brand apply — text + optional banner."""
    text = update_channel_text(channel_name=channel_name, description=description)
    if not text.ok and not banner_path:
        return text
    if banner_path:
        banner = upload_channel_banner(banner_path)
        if not banner.ok:
            return ChannelApiResult(
                ok=text.ok,
                message=f"{text.message} Banner failed: {banner.message}",
                channel_id=text.channel_id,
                name_updated=text.name_updated,
                description_updated=text.description_updated,
            )
        return ChannelApiResult(
            ok=True,
            message=f"{text.message} {banner.message}",
            channel_id=text.channel_id or banner.channel_id,
            name_updated=text.name_updated,
            description_updated=text.description_updated,
            banner_updated=True,
        )
    return text
