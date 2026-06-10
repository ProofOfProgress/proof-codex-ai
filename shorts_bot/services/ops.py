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
    is_comments_command,
    is_comments_pending_command,
    is_sync_command,
    parse_browse_request,
    parse_daily_topic,
    parse_dev_request,
    parse_auto_video_request,
    parse_finish_request,
    parse_research_request,
    parse_voice_request,
    parse_produce_request,
)
from shorts_bot.memory.agent_memory import (
    is_memory_list_request,
    parse_forget_request,
    parse_remember_request,
)
from shorts_bot.web.deps import (
    get_agent,
    get_agent_memory,
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
        browse = parse_browse_request(text)
        if browse is not None:
            target, visible = browse
            if target == "__status__":
                return self.browser_status_text()
            if visible:
                return self.open_browser(target)
            return self.browse_web(target)
        if is_memory_list_request(text):
            return self.list_agent_memory()
        forget_id = parse_forget_request(text)
        if forget_id is not None:
            return self.forget_agent_memory(forget_id)
        remembered = parse_remember_request(text)
        if remembered is not None:
            category, content = remembered
            return self.remember_agent_memory(content, category=category)
        if is_sync_command(text):
            r = self.youtube_sync()
            return r.get("message", "Sync done.")
        if is_comments_pending_command(text):
            return self.format_comments_pending()
        if is_comments_command(text):
            return self.run_comment_replies().get("message", "Done.")
        if is_apply_brand_command(text):
            r = self.apply_channel_branding()
            return r.get("message", "Brand apply done.")
        if is_daily_command(text):
            return self.run_daily_short(topic=parse_daily_topic(text))
        research_parsed = parse_research_request(text)
        if research_parsed is not None:
            topic, force_refresh = research_parsed
            if not topic:
                return "Usage: research <topic> or deep research <topic>"
            return self.run_research(topic, force_refresh=force_refresh)
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

        from shorts_bot.agents.manager import should_use_manager, ChiefManager

        if should_use_manager(text):
            return ChiefManager().handle(text).reply

        return get_agent().chat(text)

    def manager_chat(self, message: str) -> dict:
        """Chief manager with full result payload (work log, timing)."""
        from shorts_bot.agents.manager import ChiefManager

        return ChiefManager().handle(message).to_dict()

    def _help_text(self) -> str:
        return (
            "Shorts Bot commands (work in Discord DM without ! prefix too):\n"
            "• draft <topic> — script draft\n"
            "• dev: <title> | <what to build> — coding task queue\n"
            "• build: polish the web UI — same as dev:\n"
            "• pending — what needs Yes/No\n"
            "• yes <id> / no <id> — approve improvements\n"
            "• sync — YouTube Analytics (after Google login)\n"
            "• comments — auto-reply light comments; serious ones queued for you\n"
            "• comments pending — serious comments that need your reply\n"
            "• daily — full autopilot Short (research → draft → voice → render → upload)\n"
            "• daily <topic> — same with topic override\n"
            "• research <topic> — deep research (web + vidIQ + competitors + Jenny)\n"
            "• deep research <topic> — same, force refresh (re-browse web)\n"
            "• finish video <draft_id> — paid pipeline finish + upload\n"
            "• apply brand — channel name + description + banner via YouTube API\n"
            "• generate assets — profile.png + banner.png locally\n"
            "• login status — live service health\n"
            "• make video <draft_id> — auto still pack from script\n"
            "• remember <fact> — save operating rule / preference for future sessions\n"
            "• memory / rules — list what the bot remembers\n"
            "• forget <id> — remove a saved memory\n"
            "• browse <url> — headless browser, return page text\n"
            "• browser open <url|trends|youtube> — visible Desktop browser\n"
            "• browser login youtube — open login tab (saved session)\n"
            "• Or chat normally (Gemini/OpenAI)\n"
            "• Chief Manager: prefix manager: or say take 30m / [1h] before your request\n"
            "  Example: take an hour to score cosy topics and draft the best one\n"
            "• CLI: python3 -m shorts_bot.agents.cli"
        )

    def browser_status_text(self) -> str:
        from shorts_bot.browser.session import is_playwright_ready

        ok, detail = is_playwright_ready()
        mark = "✓" if ok else "✗"
        return (
            f"{mark} **Browser** — {detail}\n"
            f"Profile: `{settings.browser_profile_dir}`\n"
            "Commands: `browse <url>` · `browser open vidiq` · `browser login youtube`"
        )

    def browse_web(self, url_or_site: str) -> str:
        from shorts_bot.browser.session import browse_url

        try:
            result = browse_url(url_or_site, screenshot=settings.browser_save_screenshots)
            return result.summary()
        except Exception as exc:
            return f"Browse failed: {exc}"

    def open_browser(self, url_or_site: str) -> str:
        from shorts_bot.browser.session import open_browser_for_human

        try:
            result = open_browser_for_human(url_or_site)
            return result.message or result.summary()
        except Exception as exc:
            return f"Open browser failed: {exc}"

    def remember_agent_memory(self, content: str, *, category: str = "fact") -> str:
        mem = get_agent_memory().add_memory(content=content, category=category, source="user", pinned=False)
        return f"Saved memory #{mem.id} [{mem.category}]: {mem.content}"

    def forget_agent_memory(self, memory_id: int) -> str:
        ok = get_agent_memory().delete_memory(memory_id)
        if ok:
            return f"Forgot memory #{memory_id}."
        return f"No memory with id #{memory_id}."

    def list_agent_memory(self) -> str:
        return get_agent_memory().format_list()

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
            "pending_comments": memory.count_comments_needing_human(),
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
        from shorts_bot.learning.feedback import learn_from_draft

        d = get_store().review_draft(draft_id, "approved", note)
        learned = learn_from_draft(get_memory(), d.topic, note, "approved")
        return f"✅ Draft #{d.id} approved: {d.topic}\n{learned}"

    def reject_draft(self, draft_id: int, note: str) -> str:
        from shorts_bot.learning.feedback import learn_from_draft

        d = get_store().review_draft(draft_id, "rejected", note)
        learned = learn_from_draft(get_memory(), d.topic, note, "rejected")
        return f"Draft #{d.id} rejected. {learned}"

    def create_draft(self, topic: str, angle: str | None = None) -> str:
        result = get_agent().tool_runner.run("create_draft", {"topic": topic, "angle": angle})
        data = json.loads(result)
        return f"📝 Draft #{data.get('draft_id')} created: {data.get('topic')}\nHook: {data.get('hook')}"

    def youtube_sync(self) -> dict[str, Any]:
        from shorts_bot.web.deps import run_full_automation

        result = run_full_automation()
        r = result.sync
        msg = r.message
        extras: list[str] = []
        if result.improvements_auto_approved:
            extras.append(f"auto-approved {result.improvements_auto_approved} improvement(s)")
        if result.dev_tasks_auto_approved:
            extras.append(f"auto-approved {result.dev_tasks_auto_approved} dev task(s)")
        if result.videos_published:
            extras.append(f"published {result.videos_published} video(s)")
        if result.comments_auto_replied:
            extras.append(f"auto-replied {result.comments_auto_replied} comment(s)")
        if result.comments_queued_human:
            extras.append(f"{result.comments_queued_human} serious comment(s) for you")
        if extras:
            msg = f"{msg} ({'; '.join(extras)})"
        if result.comment_message and result.comments_auto_replied + result.comments_queued_human:
            msg += f"\n{result.comment_message}"
        return {
            "ok": r.ok,
            "message": msg,
            "videos_scored": r.videos_scored,
            "improvements_created": r.improvements_created,
            "improvements_auto_approved": result.improvements_auto_approved,
            "videos_published": result.videos_published,
            "comments_auto_replied": result.comments_auto_replied,
            "comments_queued_human": result.comments_queued_human,
        }

    def run_comment_replies(self) -> dict[str, Any]:
        from shorts_bot.comments.runner import run_comment_automation

        r = run_comment_automation(get_memory())
        return {
            "ok": r.ok,
            "message": r.message,
            "auto_replied": r.auto_replied,
            "queued_human": r.queued_human,
            "human_queue": r.human_queue,
        }

    def format_comments_pending(self) -> str:
        rows = get_memory().list_comments_needing_human(limit=12)
        if not rows:
            return "No serious comments waiting — auto-reply handled the light ones."
        lines = ["**Comments that need you** (serious / personal / medical / crisis):"]
        for row in rows:
            lines.append(
                f"• **{row['author']}** on `{row['video_id']}`: {row['original_text'][:160]}…"
                f"\n  _{row['reason']}_"
            )
        lines.append("\nReply in YouTube Studio — bot will not auto-post on these.")
        return "\n".join(lines)

    def auto_make_video(
        self,
        draft_id: int,
        *,
        generate_voice: bool | None = None,
    ) -> dict[str, Any]:
        """Full paid pipeline (Resemble + TurboScribe + render) — same as finish, no upload."""
        del generate_voice  # voice is always generated in finish_draft_pipeline
        return self.finish_video(draft_id, upload=False)

    def finish_video(self, draft_id: int, *, upload: bool | None = None) -> dict[str, Any]:
        from shorts_bot.production.pipeline import finish_draft_pipeline

        store = get_store()
        try:
            result = finish_draft_pipeline(store, draft_id, upload_youtube=upload)
        except (ValueError, KeyError, FileNotFoundError, OSError, RuntimeError) as exc:
            return {"ok": False, "message": str(exc)}
        lines = list(result.messages)
        if result.video_path:
            lines.append(f"Video: {result.video_path}")
        if result.upload_url:
            lines.append(f"Upload: {result.upload_url}")
        return {"ok": True, "message": "\n".join(lines)}

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

    def run_research(self, topic: str, *, force_refresh: bool = False) -> str:
        from shorts_bot.production.research import deep_research_topic

        r = deep_research_topic(topic, force_refresh=force_refresh)
        sources = ", ".join(r.research_sources) or "course+llm"
        header = f"Deep research saved: {topic}\nSources: {sources}"
        if r.recommended_path:
            header += f"\n\nFastest path:\n{r.recommended_path}"
        return f"{header}\n\n{r.summary_for_chat()}"

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
        from shorts_bot.brand.assets import BANNER_PATH, PROFILE_PATH, ensure_brand_assets
        from shorts_bot.youtube.channel_api import apply_brand_from_files

        brand = ChannelBrand()
        fields = brand.youtube_fields()
        name = channel_name or (fields.channel_name if use_brand_file else None)
        desc = description or (fields.description if use_brand_file else None)
        profile, banner = ensure_brand_assets()

        try:
            api = apply_brand_from_files(
                channel_name=name or None,
                description=desc or None,
                banner_path=banner if banner.exists() else BANNER_PATH,
            )
            msg = api.message
            profile_updated = False
            if settings.browser_enabled and profile.exists():
                try:
                    from shorts_bot.youtube.channel_branding import YouTubeChannelBranding

                    browser = YouTubeChannelBranding(
                        profile_dir=settings.browser_profile_dir,
                        headless=True,
                    )
                    pic = browser.upload_profile_only(profile)
                    if pic.profile_updated:
                        profile_updated = True
                        msg += f"\n\nProfile picture uploaded via Studio ({profile.name})."
                    elif pic.status == "not_logged_in":
                        msg += (
                            f"\n\nProfile: upload `{profile}` in Studio → Branding "
                            "(browser not logged in for Studio)."
                        )
                    else:
                        msg += (
                            f"\n\nProfile: upload `{profile}` manually in Studio → Branding "
                            f"({pic.message[:120]})."
                        )
                except Exception as pic_exc:
                    msg += f"\n\nProfile: upload `{profile}` in Studio → Branding ({pic_exc})."
            else:
                msg += (
                    f"\n\nProfile: upload `{profile}` in Studio → Customization → Branding."
                )
            series = fields.series or "The Minute Before"
            need_browser_text = not api.name_updated and not api.description_updated and (name or desc)
            if need_browser_text and settings.browser_enabled:
                try:
                    from shorts_bot.youtube.channel_branding import YouTubeChannelBranding

                    browser = YouTubeChannelBranding(
                        profile_dir=settings.browser_profile_dir,
                        headless=True,
                    )
                    studio = browser.apply(channel_name=name, description=desc)
                    if studio.name_updated:
                        msg += "\n\nDisplay name set via Studio browser."
                    if studio.description_updated:
                        msg += "\n\nDescription set via Studio browser."
                except Exception as studio_exc:
                    msg += f"\n\nStudio text fallback: {studio_exc}"

            return {
                "ok": api.ok or api.banner_updated,
                "status": "applied" if (api.ok or api.banner_updated) else "partial",
                "message": msg,
                "name_updated": api.name_updated,
                "description_updated": api.description_updated,
                "banner_updated": api.banner_updated,
                "profile_updated": profile_updated,
                "channel_name": name,
                "series": series,
            }
        except Exception as exc:
            scope_issue = "insufficient" in str(exc).lower() or "403" in str(exc)
            if not use_browser_fallback and (scope_issue or settings.browser_enabled):
                use_browser_fallback = True
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
        from shorts_bot.automation.auto_approve import dev_task_is_auto_approvable
        from shorts_bot.automation.coordinator import auto_approve_pending_dev_tasks

        memory = get_memory()
        task = memory.create_dev_task(title=title, description=description)
        if dev_task_is_auto_approvable(task):
            auto_approve_pending_dev_tasks(memory)
            return f"🔧 Dev task #{task.id} auto-approved: {task.title} (see data/DEV_QUEUE.md)"
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
