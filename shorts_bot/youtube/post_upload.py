"""Post-upload hooks — CTA comment + analytics sync."""

from __future__ import annotations

DEFAULT_CTA = (
    "What should the next impossible detail be? One sentence — I read every comment. "
    "🔊 jumpscare at the end."
)


def post_upload_cta_comment(video_id: str, *, text: str | None = None) -> str | None:
    """Post series CTA as top-level comment. Returns comment thread id or None."""
    from shorts_bot.youtube.comment_client import comments_ready

    if not comments_ready():
        return None
    body_text = (text or DEFAULT_CTA).strip()
    if not body_text:
        return None
    try:
        from shorts_bot.youtube.google_auth import load_credentials_for_upload
        from googleapiclient.discovery import build

        creds = load_credentials_for_upload()
        if not creds:
            return None
        yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
        body = {
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {"snippet": {"textOriginal": body_text[:9000]}},
            }
        }
        resp = yt.commentThreads().insert(part="snippet", body=body).execute()
        return resp.get("id")
    except Exception:
        return None


def sync_analytics_after_upload() -> str:
    """Best-effort analytics sync so retention data flows into learning loop."""
    try:
        from shorts_bot.memory.extensions import MemoryExtensions
        from shorts_bot.memory.store import MemoryStore
        from shorts_bot.training.proposer import ImprovementProposer
        from shorts_bot.youtube.sync import AnalyticsSync

        mem = MemoryExtensions(MemoryStore())
        result = AnalyticsSync(mem, ImprovementProposer(mem)).run(days=28, max_videos=15)
        return result.message
    except Exception as exc:
        return f"Analytics sync skipped: {exc}"[:200]
