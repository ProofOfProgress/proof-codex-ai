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
    """Set display name + description through brandingSettings.channel (needs force-ssl scope)."""
    if not channel_name and not description:
        return ChannelApiResult(False, "Nothing to update.")

    try:
        yt = _youtube()
        cid = get_my_channel_id()
        current = yt.channels().list(part="brandingSettings", id=cid).execute()
        items = current.get("items") or []
        branding = (items[0].get("brandingSettings") if items else {}) or {}
        channel_block = dict(branding.get("channel") or {})

        # YouTube forbids changing display name via API (channelTitleUpdateForbidden).
        # Omit title so description/keywords updates still work; name needs Studio.
        current_title = (channel_block.get("title") or "").strip()
        requested_name = (channel_name or "").strip()
        name_ok = False
        desc_ok = False
        if description:
            channel_block["description"] = description[:1000]
            desc_ok = True

        yt.channels().update(
            part="brandingSettings",
            body={"id": cid, "brandingSettings": {"channel": channel_block}},
        ).execute()

        parts = []
        if desc_ok:
            parts.append("description")
        name_note = ""
        if requested_name and requested_name != current_title:
            name_note = (
                f" Display name still '{current_title}' — YouTube API cannot rename channels; "
                f"use Studio to set '{requested_name}' (or an alternate if taken)."
            )
        elif requested_name and requested_name == current_title:
            name_ok = True
            parts.append("name (unchanged)")

        msg = f"Channel {' + '.join(parts)} updated via API." if parts else "No API fields updated."
        return ChannelApiResult(
            ok=bool(parts),
            message=(msg + name_note).strip(),
            channel_id=cid,
            name_updated=name_ok,
            description_updated=desc_ok,
        )
    except Exception as exc:  # noqa: BLE001
        hint = "Re-auth: YOUTUBE_OAUTH_UPLOAD=1 python3 -m shorts_bot.youtube.auth_cli"
        if "insufficient" in str(exc).lower() or "403" in str(exc):
            return ChannelApiResult(
                False,
                f"Name/description need youtube.force-ssl on token ({exc}). {hint}",
            )
        return ChannelApiResult(False, f"Channel text update failed: {exc}")


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
    """API brand apply — banner (upload scope) + text (force-ssl scope). Partial OK."""
    text = (
        update_channel_text(channel_name=channel_name, description=description)
        if channel_name or description
        else ChannelApiResult(True, "No text fields to update.")
    )
    banner = (
        upload_channel_banner(banner_path)
        if banner_path
        else ChannelApiResult(True, "No banner to upload.")
    )

    ok = text.ok or banner.ok
    parts = [p for p in (text.message, banner.message) if p and "No " not in p]
    message = " ".join(parts).strip() or "Nothing updated."

    return ChannelApiResult(
        ok=ok,
        message=message,
        channel_id=text.channel_id or banner.channel_id,
        name_updated=text.name_updated,
        description_updated=text.description_updated,
        banner_updated=banner.banner_updated,
    )
