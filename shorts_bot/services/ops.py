from __future__ import annotations

import json
from typing import Any

from shorts_bot.config import settings
from shorts_bot.learning.learned_file import LearnedFile
from shorts_bot.services.chat_router import (
    is_apply_brand_command,
    is_help_command,
    is_pending_command,
    is_sync_command,
    parse_dev_request,
)
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
        text = message.strip()
        if not text:
            return "Say something — draft ideas, dev: build X, or sync (after YouTube login)."

        if is_help_command(text):
            return self._help_text()
        if is_sync_command(text):
            r = self.youtube_sync()
            return r.get("message", "Sync done.")
        if is_apply_brand_command(text):
            r = self.apply_channel_branding()
            return r.get("message", "Brand apply done.")
        if is_pending_command(text):
            return self._format_pending()
        dev = parse_dev_request(text)
        if dev:
            title, desc = dev
            return self.create_dev_task(title, desc)

        lower = text.lower()
        if lower.startswith("draft "):
            return self.create_draft(text[6:].strip())
        if lower.startswith("yes ") and lower.split()[1:2]:
            try:
                return self.approve_improvement(int(text.split()[1]))
            except (ValueError, IndexError):
                pass
        if lower.startswith("no ") and lower.split()[1:2]:
            try:
                return self.reject_improvement(int(text.split()[1]))
            except (ValueError, IndexError):
                pass
        if lower.startswith("yes dev "):
            try:
                return self.approve_dev_task(int(text.split()[2]))
            except (ValueError, IndexError):
                pass
        if lower.startswith("no dev "):
            try:
                return self.reject_dev_task(int(text.split()[2]))
            except (ValueError, IndexError):
                pass

        return get_agent().chat(text)

    def _help_text(self) -> str:
        return (
            "Shorts Bot commands (work in Discord DM without ! prefix too):\n"
            "• draft <topic> — script draft\n"
            "• dev: <title> | <what to build> — coding task queue\n"
            "• build: polish the web UI — same as dev:\n"
            "• pending — what needs Yes/No\n"
            "• yes <id> / no <id> — approve improvements\n"
            "• sync — YouTube Analytics (after Google login)\n"
            "• apply brand — update channel name + description in Studio\n"
            "• Or just chat normally (needs OpenAI key for full mode)"
        )

    def _format_pending(self) -> str:
        imps = self.list_improvements()
        drafts = self.list_drafts()
        dev = self.list_dev_tasks()
        lines = ["**Needs your Yes/No:**"]
        for i in imps[:6]:
            lines.append(f"Improvement #{i['id']}: {i['title']} — yes {i['id']} / no {i['id']}")
        for d in drafts[:4]:
            lines.append(f"Draft #{d['id']}: {d['topic']}")
        for t in dev[:4]:
            lines.append(f"Dev #{t['id']}: {t['title']}")
        if len(lines) == 1:
            return "All caught up — nothing pending."
        lines.append("\nWeb: http://localhost:8080 (one-tap buttons)")
        return "\n".join(lines)

    def setup_checklist(self) -> list[dict[str, Any]]:
        yt = auth_status()
        items = [
            {
                "id": "discord",
                "label": "Discord bot",
                "done": settings.has_discord,
                "action": "DISCORD_BOT_TOKEN in .env",
            },
            {
                "id": "openai",
                "label": "Full AI chat (optional)",
                "done": settings.has_openai,
                "action": "docs/CHAT_TONIGHT.md",
            },
            {
                "id": "google_keys",
                "label": "Google API keys",
                "done": bool(yt.get("credentials_configured")),
                "action": "docs/TOMORROW.md step 1",
            },
            {
                "id": "youtube_oauth",
                "label": "YouTube sign-in (once)",
                "done": bool(yt.get("token_saved")),
                "action": "python3 -m shorts_bot.youtube.auth_cli",
            },
        ]
        return items

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
            "checklist": self.setup_checklist(),
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
        return f"✅ Approved: {imp.title}"

    def reject_improvement(self, improvement_id: int, note: str = "Skipped.") -> str:
        imp = get_memory().review_improvement(improvement_id, approved=False, note=note)
        return f"Skipped: {imp.title}"

    def list_drafts(self) -> list[dict[str, Any]]:
        store = get_store()
        return [
            {"id": d.id, "topic": d.topic, "hook": d.hook, "script": d.script}
            for d in store.list_drafts(status="pending")
        ]

    def approve_draft(self, draft_id: int, note: str = "Approved.") -> str:
        d = get_store().review_draft(draft_id, "approved", note)
        get_proposer().propose_from_feedback(d.topic, note, "approved")
        return f"✅ Draft #{d.id} approved: {d.topic}"

    def reject_draft(self, draft_id: int, note: str) -> str:
        d = get_store().review_draft(draft_id, "rejected", note)
        get_proposer().propose_from_feedback(d.topic, note, "rejected")
        return f"Draft #{d.id} rejected."

    def create_draft(self, topic: str, angle: str | None = None) -> str:
        result = get_agent().tool_runner.run("create_draft", {"topic": topic, "angle": angle})
        data = json.loads(result)
        return f"📝 Draft #{data.get('draft_id')} created: {data.get('topic')}\nHook: {data.get('hook')}"

    def youtube_sync(self) -> dict[str, Any]:
        r = get_analytics_sync().run()
        return {
            "ok": r.ok,
            "message": r.message,
            "videos_scored": r.videos_scored,
            "improvements_created": r.improvements_created,
        }

    def apply_channel_branding(
        self,
        *,
        channel_name: str | None = None,
        description: str | None = None,
        use_brand_file: bool = True,
    ) -> dict[str, Any]:
        from shorts_bot.youtube.channel_branding import YouTubeChannelBranding

        operator = YouTubeChannelBranding(
            profile_dir=settings.browser_profile_dir,
            headless=False,
        )
        if use_brand_file and not channel_name and not description:
            result = operator.apply_from_brand_file()
        else:
            result = operator.apply(channel_name=channel_name, description=description)
        return {
            "ok": result.status in {"applied", "partial"},
            "status": result.status,
            "message": result.message,
            "name_updated": result.name_updated,
            "description_updated": result.description_updated,
            "channel_name": result.channel_name,
            "screenshot": result.screenshot_path,
            "url": result.current_url,
        }

    def recent_rewards(self, limit: int = 8) -> list[dict[str, Any]]:
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
        return f"🔧 Dev task #{task.id} queued: {task.title}\nApprove: yes dev {task.id} or web UI"

    def approve_dev_task(self, task_id: int, note: str = "Approved.") -> str:
        task = get_memory().review_dev_task(task_id, approved=True, note=note)
        LearnedFile(settings.learned_path).record_dev_task(task, approved=True)
        return f"✅ Dev approved: {task.title}"

    def reject_dev_task(self, task_id: int, note: str = "Rejected.") -> str:
        task = get_memory().review_dev_task(task_id, approved=False, note=note)
        return f"Dev skipped: {task.title}"

    def score_preview(self, video_label: str, metrics: dict[str, Any]) -> dict[str, Any]:
        result = get_reward_engine().score(video_label, metrics)
        return {
            "score": result.score,
            "verdict": result.verdict,
            "reason": result.reason,
            "diagnosis": result.diagnosis,
            "breakdown": result.breakdown,
        }
