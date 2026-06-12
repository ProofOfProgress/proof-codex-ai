"""Post-upload hooks — CTA comment + analytics sync."""

from __future__ import annotations

# Pinned/CTA comments: simple story ideas only — no ending spoilers.
CTA_NO_SPOILER_RULE = (
    "Do not mention jumpscare, scare at the end, loud ending, headphones, or volume in comments."
)

DEFAULT_CTA = (
    "What scary story should we do next? Write one sentence. I read every comment."
)

_ALTERNATE_CTAS = (
    "What story should we make next? One sentence.",
    "What did you spot the second time you watched? One line.",
    "Drop your next story idea in one sentence.",
)


def pick_cta_comment(*, draft_id: int = 0) -> str:
    """Rotate engagement CTAs — never spoil the scare."""
    if draft_id <= 0:
        return DEFAULT_CTA
    return _ALTERNATE_CTAS[draft_id % len(_ALTERNATE_CTAS)]


def _cta_is_safe(text: str) -> bool:
    lower = text.lower()
    banned = (
        "jumpscare",
        "jump scare",
        "scare at the end",
        "at the end",
        "near the end",
        "last second",
        "last 3",
        "volume warning",
        "headphones",
        "loud ending",
        "turn your volume",
        "impossible detail",
    )
    return not any(b in lower for b in banned)


def post_upload_cta_comment(
    video_id: str,
    *,
    text: str | None = None,
    draft_id: int = 0,
) -> str | None:
    """Post series CTA as top-level comment. Returns comment thread id or None."""
    from shorts_bot.youtube.comment_client import comments_ready

    if not comments_ready():
        return None
    body_text = (text or pick_cta_comment(draft_id=draft_id)).strip()
    if not body_text or not _cta_is_safe(body_text):
        body_text = DEFAULT_CTA
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

        from shorts_bot.config import settings

        mem = MemoryExtensions(MemoryStore(settings.database_path))
        result = AnalyticsSync(mem, ImprovementProposer(mem)).run(days=28, max_videos=15)
        return result.message
    except Exception as exc:
        return f"Analytics sync skipped: {exc}"[:200]
