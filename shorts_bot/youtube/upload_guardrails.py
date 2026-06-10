"""Shared upload guardrails — API + Studio browser uploads."""

from __future__ import annotations

import re
from dataclasses import dataclass

from shorts_bot.compliance.upload_guard import check_upload_allowed
from shorts_bot.config import settings
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore


@dataclass
class UploadPreflight:
    allowed: bool
    message: str
    existing_video_ids: list[str]


def _normalize_title(title: str) -> str:
    t = re.sub(r"\s+", " ", title.strip().lower())
    t = re.sub(r"\s*\(v\d+[^)]*\)\s*$", "", t)
    return t


def uploads_for_draft(memory: MemoryExtensions, draft_id: int) -> list[dict]:
    with memory._conn() as conn:
        rows = conn.execute(
            """
            SELECT draft_id, topic, hook, title, video_id, uploaded_at
            FROM upload_events
            WHERE draft_id = ?
            ORDER BY id DESC
            """,
            (draft_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def channel_videos_matching_title(title: str) -> list[str]:
    """Return video IDs on channel with same normalized title (YouTube API readonly)."""
    try:
        from shorts_bot.youtube.channel_videos import list_channel_videos
    except Exception:
        return []
    target = _normalize_title(title)
    if not target:
        return []
    ids: list[str] = []
    for v in list_channel_videos(max_results=50):
        if _normalize_title(v.title) == target or target in _normalize_title(v.title):
            ids.append(v.video_id)
    return ids


def preflight_upload(
    store: MemoryStore,
    memory: MemoryExtensions,
    *,
    draft_id: int,
    topic: str,
    hook: str,
    script: str,
    title: str,
    allow_duplicate_draft: bool = False,
) -> UploadPreflight:
    """
    Run YPP guard + duplicate draft/title checks before any upload path (API or Studio).
    """
    existing_ids: list[str] = []

    if settings.block_duplicate_draft_upload and not allow_duplicate_draft:
        prior = uploads_for_draft(memory, draft_id)
        for row in prior:
            vid = row.get("video_id")
            if vid:
                existing_ids.append(vid)
        if existing_ids:
            return UploadPreflight(
                False,
                f"Draft #{draft_id} already uploaded as {', '.join(existing_ids)}. "
                "Delete duplicates in Studio first or pass allow_duplicate_draft=True.",
                existing_ids,
            )

    if settings.block_duplicate_title_upload:
        on_channel = channel_videos_matching_title(title)
        for vid in on_channel:
            if vid not in existing_ids:
                existing_ids.append(vid)
        if on_channel:
            return UploadPreflight(
                False,
                f"Channel already has this title ({len(on_channel)} video(s)): "
                f"{', '.join(on_channel[:5])}. Not uploading again.",
                existing_ids,
            )

    compliance = check_upload_allowed(
        store,
        memory,
        draft_id=draft_id,
        topic=topic,
        hook=hook,
        script=script,
        title=title,
    )
    if not compliance.allowed:
        return UploadPreflight(False, compliance.summary(), existing_ids)
    warn = f" {compliance.summary()}" if compliance.warnings else ""
    return UploadPreflight(True, f"Upload preflight OK.{warn}", existing_ids)
