"""Run comment fetch → triage → auto-reply or human queue."""

from __future__ import annotations

from dataclasses import dataclass, field

from shorts_bot.comments.reply import generate_reply
from shorts_bot.comments.triage import triage_comment
from shorts_bot.config import settings
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.youtube.comment_client import (
    CommentThread,
    comments_ready,
    fetch_recent_threads,
    post_reply,
)


@dataclass
class CommentRunResult:
    ok: bool
    message: str
    scanned: int = 0
    auto_replied: int = 0
    queued_human: int = 0
    skipped: int = 0
    human_queue: list[dict] = field(default_factory=list)


def run_comment_automation(memory: MemoryExtensions) -> CommentRunResult:
    if not settings.auto_reply_comments:
        return CommentRunResult(ok=True, message="Comment auto-reply disabled (AUTO_REPLY_COMMENTS=false).")

    if not comments_ready():
        return CommentRunResult(
            ok=False,
            message="YouTube OAuth missing for comments. Re-auth with YOUTUBE_OAUTH_UPLOAD=1.",
        )

    try:
        threads = fetch_recent_threads(max_results=settings.comment_fetch_max)
    except Exception as exc:  # noqa: BLE001
        return CommentRunResult(ok=False, message=f"Comment fetch failed: {exc}")

    auto_n = 0
    human_n = 0
    skip_n = 0
    human_queue: list[dict] = []
    my_cid = None

    try:
        from shorts_bot.youtube.channel_api import get_my_channel_id

        my_cid = get_my_channel_id()
    except Exception:
        pass

    for thread in threads:
        if _should_skip_thread(thread, memory, my_channel_id=my_cid):
            skip_n += 1
            continue

        triage = triage_comment(thread.text, author=thread.author)
        if triage.decision == "skip":
            memory.record_comment_action(
                comment_id=thread.top_comment_id,
                video_id=thread.video_id,
                author=thread.author,
                original_text=thread.text,
                decision="skipped",
                reason=triage.reason,
            )
            skip_n += 1
            continue

        if triage.decision == "spam":
            memory.record_comment_action(
                comment_id=thread.top_comment_id,
                video_id=thread.video_id,
                author=thread.author,
                original_text=thread.text,
                decision="spam",
                reason=triage.reason,
            )
            skip_n += 1
            continue

        if triage.decision == "human":
            memory.record_comment_action(
                comment_id=thread.top_comment_id,
                video_id=thread.video_id,
                author=thread.author,
                original_text=thread.text,
                decision="needs_human",
                reason=triage.reason,
            )
            human_n += 1
            human_queue.append(
                {
                    "author": thread.author,
                    "text": thread.text[:300],
                    "video": thread.video_title[:80],
                    "reason": triage.reason,
                }
            )
            continue

        if auto_n >= settings.comment_max_auto_per_run:
            continue

        reply_text = generate_reply(thread.text, video_title=thread.video_title)
        try:
            post_reply(thread.top_comment_id, reply_text)
            memory.record_comment_action(
                comment_id=thread.top_comment_id,
                video_id=thread.video_id,
                author=thread.author,
                original_text=thread.text,
                decision="auto_replied",
                reason=triage.reason,
                reply_text=reply_text,
            )
            auto_n += 1
        except Exception as exc:  # noqa: BLE001
            memory.record_comment_action(
                comment_id=thread.top_comment_id,
                video_id=thread.video_id,
                author=thread.author,
                original_text=thread.text,
                decision="needs_human",
                reason=f"post failed: {exc}",
            )
            human_n += 1
            human_queue.append(
                {
                    "author": thread.author,
                    "text": thread.text[:300],
                    "video": thread.video_title[:80],
                    "reason": f"auto-reply failed: {exc}",
                }
            )

    msg = (
        f"Comments: scanned {len(threads)}, auto-replied {auto_n}, "
        f"queued for you {human_n}, skipped {skip_n}."
    )
    if human_n:
        msg += " Say `comments pending` to review serious ones."

    return CommentRunResult(
        ok=True,
        message=msg,
        scanned=len(threads),
        auto_replied=auto_n,
        queued_human=human_n,
        skipped=skip_n,
        human_queue=human_queue,
    )


def _should_skip_thread(
    thread: CommentThread,
    memory: MemoryExtensions,
    *,
    my_channel_id: str | None,
) -> bool:
    if memory.comment_already_handled(thread.top_comment_id):
        return True
    if thread.channel_has_replied:
        return True
    if my_channel_id and thread.author_channel_id == my_channel_id:
        return True
    return False
