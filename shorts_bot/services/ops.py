from __future__ import annotations

from typing import Any

from shorts_bot.config import settings
from shorts_bot.learning.learned_file import LearnedFile
from shorts_bot.web.deps import (
    get_agent,
    get_analytics_sync,
    get_memory,
    get_proposer,
    get_reward_engine,
    get_store,
)
from shorts_bot.youtube.google_auth import auth_status


class BotOperations:
    """Shared operations for web UI and Discord."""

    def chat(self, message: str) -> str:
        return get_agent().chat(message.strip())

    def status(self) -> dict[str, Any]:
        store = get_store()
        memory = get_memory()
        yt = auth_status()
        return {
            "openai": settings.has_openai,
            "discord": settings.has_discord,
            "channel": store.channel_summary(),
            "stats": store.stats(),
            "pending_improvements": len(memory.list_improvements(status="pending")),
            "pending_drafts": len(store.list_drafts(status="pending")),
            "pending_dev": len(memory.list_dev_tasks(status="pending")),
            "applied_training": memory.applied_improvements(),
            "youtube": yt,
        }

    def list_improvements(self) -> list[dict[str, Any]]:
        memory = get_memory()
        return [
            {
                "id": i.id,
                "title": i.title,
                "category": i.category,
                "description": i.description,
                "pros": i.pros,
                "cons": i.cons,
            }
            for i in memory.list_improvements(status="pending")
        ]

    def approve_improvement(self, improvement_id: int, note: str = "Approved.") -> str:
        imp = get_memory().review_improvement(improvement_id, approved=True, note=note)
        LearnedFile(settings.learned_path).record_improvement(imp, approved=True)
        return f"Approved: {imp.title}"

    def reject_improvement(self, improvement_id: int, note: str = "Skipped.") -> str:
        imp = get_memory().review_improvement(improvement_id, approved=False, note=note)
        return f"Skipped: {imp.title}"

    def list_drafts(self) -> list[dict[str, Any]]:
        store = get_store()
        return [
            {"id": d.id, "topic": d.topic, "hook": d.hook}
            for d in store.list_drafts(status="pending")
        ]

    def approve_draft(self, draft_id: int, note: str = "Approved.") -> str:
        d = get_store().review_draft(draft_id, "approved", note)
        get_proposer().propose_from_feedback(d.topic, note, "approved")
        return f"Draft #{d.id} approved: {d.topic}"

    def reject_draft(self, draft_id: int, note: str) -> str:
        d = get_store().review_draft(draft_id, "rejected", note)
        get_proposer().propose_from_feedback(d.topic, note, "rejected")
        return f"Draft #{d.id} rejected."

    def create_draft(self, topic: str, angle: str | None = None) -> str:
        import json

        result = get_agent().tool_runner.run("create_draft", {"topic": topic, "angle": angle})
        data = json.loads(result)
        return f"Draft #{data.get('draft_id')} created: {data.get('topic')}"

    def youtube_sync(self) -> dict[str, Any]:
        r = get_analytics_sync().run()
        return {
            "ok": r.ok,
            "message": r.message,
            "videos_scored": r.videos_scored,
            "improvements_created": r.improvements_created,
        }

    def recent_rewards(self, limit: int = 5) -> list[dict[str, Any]]:
        return get_memory().recent_rewards(limit=limit)

    def learning_journal(self, limit: int = 15) -> list[dict[str, Any]]:
        return get_memory().learning_journal(limit=limit)

    def list_dev_tasks(self) -> list[dict[str, Any]]:
        return [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "pros": t.pros,
                "cons": t.cons,
            }
            for t in get_memory().list_dev_tasks(status="pending")
        ]

    def create_dev_task(self, title: str, description: str) -> str:
        task = get_memory().create_dev_task(title=title, description=description)
        return f"Dev task #{task.id} queued: {task.title}"

    def approve_dev_task(self, task_id: int, note: str = "Approved.") -> str:
        task = get_memory().review_dev_task(task_id, approved=True, note=note)
        LearnedFile(settings.learned_path).record_dev_task(task, approved=True)
        return f"Dev task approved: {task.title}"

    def reject_dev_task(self, task_id: int, note: str = "Rejected.") -> str:
        task = get_memory().review_dev_task(task_id, approved=False, note=note)
        return f"Dev task skipped: {task.title}"

    def score_preview(self, video_label: str, metrics: dict[str, Any]) -> dict[str, Any]:
        result = get_reward_engine().score(video_label, metrics)
        return {
            "score": result.score,
            "verdict": result.verdict,
            "reason": result.reason,
            "diagnosis": result.diagnosis,
            "breakdown": result.breakdown,
        }
