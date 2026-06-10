from __future__ import annotations

import json
from typing import Any

from shorts_bot.config import settings
from shorts_bot.learning.learned_file import LearnedFile
from shorts_bot.services.chat_router import (
    is_apply_brand_command,
    is_daily_command,
    is_generate_assets_command,
    is_help_command,
    is_login_status_command,
    is_pending_command,
    is_sync_command,
    parse_daily_topic,
    parse_dev_request,
    parse_auto_video_request,
    parse_finish_request,
    parse_research_request,
    parse_voice_request,
    parse_produce_request,
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
        if is_daily_command(text):
            return self.run_daily_short(topic=parse_daily_topic(text))
        research_topic = parse_research_request(text)
        if research_topic is not None:
            return self.run_research(research_topic)
        if is_login_status_command(text):
            return self.login_status_text()
        if is_generate_assets_command(text):
            return self.generate_brand_assets()
        auto_id = parse_auto_video_request(text)
        if auto_id is not None:
            if auto_id < 0:
                return "Usage: make video <draft_id>  (e.g. make video 6)"
            r = self.auto_make_video(auto_id)
            return r.get("message", "Done.")

        voice_id = parse_voice_request(text)
        if voice_id is not None:
            r = self.generate_voiceover(voice_id)
            return r.get("message", "Done.")

        finish_id = parse_finish_request(text)
        if finish_id is not None:
            return self.finish_video(finish_id).get("message", "Done.")

        produce = parse_produce_request(text)
        if produce:
            draft_id, transcript = produce
            if not transcript:
                return (
                    f"Paste TurboScribe transcript after draft id.\n"
                    f"Example: produce {draft_id} | 0:00 line one\\n0:07 line two"
                )
            r = self.prepare_video_production(draft_id, transcript)
            return r.get("message", "Done.")
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
            "• daily — full autopilot Short (research → draft → voice → render → upload)\n"
            "• daily <topic> — same with topic override\n"
            "• research <topic> — deep production research (cached)\n"
            "• finish video <draft_id> — paid pipeline finish + upload\n"
            "• apply brand — channel name + description + banner via YouTube API\n"
            "• generate assets — profile.png + banner.png locally\n"
            "• login status — live service health\n"
            "• make video <draft_id> — auto still pack from script\n"
            "• Or chat normally (Gemini/OpenAI)"
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
                "id": "chat",
                "label": "Full AI chat (Gemini free or OpenAI)",
                "done": settings.has_full_chat,
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
            "openai": settings.has_full_chat,
            "chat_provider": settings.chat_provider,
            "gemini": settings.has_gemini,
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

    def auto_make_video(
        self,
        draft_id: int,
        *,
        generate_voice: bool | None = None,
    ) -> dict[str, Any]:
        from shorts_bot.production.pack import auto_produce_draft

        store = get_store()
        try:
            pack = auto_produce_draft(store, draft_id, render_images=True)
        except (ValueError, KeyError) as exc:
            return {"ok": False, "message": str(exc)}
        if generate_voice is None:
            generate_voice = settings.auto_generate_voice

        voice_note = "record VOICEOVER_SCRIPT.txt"
        if generate_voice:
            voice = self.generate_voiceover(draft_id)
            if voice.get("ok"):
                voice_note = f"use {voice.get('output_path')} (TTS) or re-record your own voice"
            else:
                voice_note = f"TTS failed ({voice.get('message')}) — record VOICEOVER_SCRIPT.txt"
        return {
            "ok": True,
            "message": (
                f"{pack.message}\n"
                f"Next: {voice_note} → CapCut import images/ + audio → upload."
            ),
            "draft_id": pack.draft_id,
            "image_count": pack.image_count,
            "images_rendered": pack.images_rendered,
            "output_dir": str(pack.output_dir),
        }

    def finish_video(self, draft_id: int) -> dict[str, Any]:
        from shorts_bot.production.finish_cli import finish_draft

        try:
            msg = finish_draft(draft_id)
        except (ValueError, KeyError, FileNotFoundError, OSError) as exc:
            return {"ok": False, "message": str(exc)}
        return {"ok": True, "message": msg}

    def generate_voiceover(self, draft_id: int) -> dict[str, Any]:
        from shorts_bot.production.voiceover import generate_voiceover as gen_vo

        store = get_store()
        pack_dir = settings.data_dir / "production" / f"draft_{draft_id}"
        try:
            draft = store.get_draft(draft_id)
            script_path = pack_dir / "VOICEOVER_SCRIPT.txt"
            script = script_path.read_text(encoding="utf-8") if script_path.exists() else draft.script
            result = gen_vo(pack_dir, draft_id=draft_id, script_text=script)
        except (ValueError, KeyError, OSError) as exc:
            return {"ok": False, "message": str(exc)}
        return {
            "ok": True,
            "message": result.message,
            "output_path": str(result.output_path),
            "voice": result.voice,
            "duration_hint": result.duration_hint,
        }

    def prepare_video_production(self, draft_id: int, turboscribe_text: str) -> dict[str, Any]:
        from shorts_bot.production.pack import build_production_pack

        store = get_store()
        try:
            pack = build_production_pack(
                store,
                draft_id=draft_id,
                turboscribe_text=turboscribe_text,
            )
        except (ValueError, KeyError) as exc:
            return {"ok": False, "message": str(exc)}
        return {
            "ok": True,
            "message": pack.message,
            "draft_id": pack.draft_id,
            "image_count": pack.image_count,
            "output_dir": str(pack.output_dir),
        }

    def run_daily_short(self, topic: str | None = None) -> str:
        from shorts_bot.production.daily_cli import run_daily

        try:
            return run_daily(topic=topic)
        except Exception as exc:
            return f"Daily pipeline failed: {exc}"

    def run_research(self, topic: str) -> str:
        from shorts_bot.production.research import deep_research_topic

        r = deep_research_topic(topic)
        return f"Research saved for: {topic}\n\n{r.draft_context()[:1800]}"

    def login_status_text(self) -> str:
        from shorts_bot.login_status import full_status

        lines = ["**Soft Continuity — service status**"]
        for row in full_status(include_studio=False):
            mark = "✓" if row["ready"] else "✗"
            lines.append(f"{mark} **{row['label']}** — {row['detail'][:100]}")
        return "\n".join(lines)

    def generate_brand_assets(self) -> str:
        from shorts_bot.brand.assets import ensure_brand_assets

        profile, banner = ensure_brand_assets()
        return (
            f"Generated brand assets:\n"
            f"• Profile: `{profile}` (upload manually in Studio → Branding → picture)\n"
            f"• Banner: `{banner}` (API upload via `apply brand`)"
        )

    def apply_channel_branding(
        self,
        *,
        channel_name: str | None = None,
        description: str | None = None,
        use_brand_file: bool = True,
        use_browser_fallback: bool = False,
    ) -> dict[str, Any]:
        from shorts_bot.brand.loader import ChannelBrand
        from shorts_bot.brand.assets import BANNER_PATH, ensure_brand_assets
        from shorts_bot.youtube.channel_api import apply_brand_from_files

        brand = ChannelBrand()
        fields = brand.youtube_fields()
        name = channel_name or (fields.channel_name if use_brand_file else None)
        desc = description or (fields.description if use_brand_file else None)
        ensure_brand_assets()

        try:
            api = apply_brand_from_files(
                channel_name=name or None,
                description=desc or None,
                banner_path=BANNER_PATH if BANNER_PATH.exists() else None,
            )
            msg = api.message
            msg += (
                "\n\nProfile picture: upload `channel/brand/assets/profile.png` in "
                "Studio → Customization → Branding (API cannot set avatar yet)."
            )
            return {
                "ok": api.ok,
                "status": "applied" if api.ok else "failed",
                "message": msg,
                "name_updated": api.name_updated,
                "description_updated": api.description_updated,
                "channel_name": name,
            }
        except Exception as exc:
            if not use_browser_fallback:
                return {
                    "ok": False,
                    "status": "failed",
                    "message": (
                        f"YouTube API brand update failed: {exc}\n"
                        "Re-auth: YOUTUBE_OAUTH_UPLOAD=1 python3 -m shorts_bot.youtube.auth_cli"
                    ),
                }
            from shorts_bot.youtube.channel_branding import YouTubeChannelBranding

            operator = YouTubeChannelBranding(
                profile_dir=settings.browser_profile_dir,
                headless=True,
            )
            if use_brand_file and not channel_name and not description:
                result = operator.apply_from_brand_file()
            else:
                result = operator.apply(channel_name=name, description=desc)
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
