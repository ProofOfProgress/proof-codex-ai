"""Schedule YouTube Short publish via API (private until publishAt)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def upload_scheduled_short(
    draft_id: int,
    video_path: Path,
    *,
    publish_at: datetime,
) -> str:
    from shorts_bot.config import settings
    from shorts_bot.memory.extensions import MemoryExtensions
    from shorts_bot.memory.store import MemoryStore
    from shorts_bot.production.upload_meta import build_upload_package, write_upload_files
    from shorts_bot.youtube.upload_guardrails import preflight_upload

    if publish_at.tzinfo is None:
        publish_at = publish_at.replace(tzinfo=timezone.utc)
    publish_at = publish_at.astimezone(timezone.utc)

    store = MemoryStore(settings.database_path)
    mem = MemoryExtensions(store)
    draft = store.get_draft(draft_id)
    root = settings.data_dir / "production" / f"draft_{draft_id}"
    package = build_upload_package(draft.topic, draft.hook, draft_id=draft_id)
    title = package.title.replace("🔊 ", "").strip()
    if not title.startswith("🔊"):
        title = title[:100]
    package.title = title[:100]
    write_upload_files(root, package, draft_id=draft_id)

    pre = preflight_upload(
        store,
        mem,
        draft_id=draft_id,
        topic=draft.topic,
        hook=draft.hook,
        script=draft.script,
        title=package.title,
        visibility="private",
    )
    if not pre.allowed:
        raise RuntimeError(f"Upload blocked: {pre.message}")

    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    from shorts_bot.youtube.google_auth import load_credentials_for_upload

    creds = load_credentials_for_upload()
    if not creds:
        raise RuntimeError("YouTube upload not authorized")

    youtube = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": package.title[:100],
            "description": package.description[:5000],
            "tags": package.tags[:30],
            "categoryId": (settings.youtube_category_id or "28")[:2],
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "selfDeclaredMadeForKids": False,
        },
    }
    if settings.youtube_declare_synthetic_media:
        body["status"]["containsSyntheticMedia"] = True

    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()
    vid = response["id"]
    url = f"https://youtube.com/shorts/{vid}"

    from shorts_bot.compliance.upload_guard import record_upload

    record_upload(
        mem,
        draft_id=draft_id,
        topic=draft.topic,
        hook=draft.hook,
        script=draft.script,
        title=package.title,
        video_id=vid,
        extra_snapshot={
            "visibility": "scheduled",
            "publish_at": publish_at.isoformat(),
            "source_file": video_path.name,
            "brand": "Rapid Tool Review",
        },
    )
    store.review_draft(draft_id, "approved", f"scheduled {publish_at.isoformat()}")
    return url
