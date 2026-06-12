from __future__ import annotations

import json
from typing import Any, Callable

from shorts_bot.approval.queue import ApprovalQueue
from shorts_bot.config import settings
from shorts_bot.course.router import CourseRouter
from shorts_bot.drafts.generator import DraftGenerator
from shorts_bot.memory.store import MemoryStore
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.rewards.engine import RewardEngine
from shorts_bot.training.proposer import ImprovementProposer
from shorts_bot.youtube.channel_branding import YouTubeChannelBranding
from shorts_bot.youtube.channel_setup import YouTubeChannelSetup
from shorts_bot.youtube.studio import check_studio

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "create_draft",
            "description": "Create a new Short script draft and add it to the approval queue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "What the Short is about."},
                    "angle": {
                        "type": "string",
                        "description": "Optional specific angle or takeaway.",
                    },
                },
                "required": ["topic"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_pending_drafts",
            "description": "List drafts waiting for human approval.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "show_draft",
            "description": "Show full details for a draft by ID.",
            "parameters": {
                "type": "object",
                "properties": {"draft_id": {"type": "integer"}},
                "required": ["draft_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "approve_draft",
            "description": "Approve a draft for future production/posting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "draft_id": {"type": "integer"},
                    "note": {"type": "string", "description": "Optional approval note."},
                },
                "required": ["draft_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reject_draft",
            "description": "Reject a draft. Reason is required and will be learned from.",
            "parameters": {
                "type": "object",
                "properties": {
                    "draft_id": {"type": "integer"},
                    "reason": {"type": "string"},
                },
                "required": ["draft_id", "reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learned_feedback",
            "description": "Show recent approval/rejection feedback the bot should learn from.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stats",
            "description": "Show counts of pending, approved, and rejected drafts.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_course_guidance",
            "description": "Route to Jenny Hoyos course files and return relevant guidance for a question or problem.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The creator's question or problem."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_free_tools",
            "description": "List free and free-tier services for editing, music, design, and storage.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "score_video_performance",
            "description": "Score a published Short vs benchmarks; may create improvement proposal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "video_label": {"type": "string"},
                    "viewed_vs_swiped_away": {"type": "number"},
                    "retention_rate": {"type": "number"},
                    "views": {"type": "integer"},
                    "likes": {"type": "integer"},
                    "comments": {"type": "integer"},
                },
                "required": ["video_label"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_channel_brand",
            "description": "Get Don't Blink channel brand voice, YouTube copy, and niche guidance.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "queue_dev_task",
            "description": "Queue a coding/development task for human Yes/No approval before work runs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["title", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_pending_improvements",
            "description": "List self-improvement proposals waiting for human Yes/No.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sync_youtube_analytics",
            "description": (
                "Pull official YouTube Analytics for recent videos, score performance, "
                "and create improvement proposals for human Yes/No approval."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_youtube_status",
            "description": "Check if YouTube channel is set up and Studio is accessible.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mark_channel_ready",
            "description": "Record that the human finished channel setup (name, handle, etc.).",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel_name": {"type": "string"},
                    "note": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "apply_channel_branding",
            "description": (
                "Update YouTube channel display name and description in Studio "
                "from channel/brand/youtube_copy.txt (or explicit overrides). "
                "Requires saved browser login."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "channel_name": {
                        "type": "string",
                        "description": "Optional override for display name.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional override for channel description.",
                    },
                    "use_brand_file": {
                        "type": "boolean",
                        "description": "Use youtube_copy.txt when true (default).",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prepare_video_production",
            "description": (
                "Build timestamped still-image production pack from TurboScribe transcript: "
                "one image prompt per timestamp, CapCut timeline, manifest for Don't Blink Shorts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "draft_id": {"type": "integer", "description": "Draft ID with approved script."},
                    "turboscribe_text": {
                        "type": "string",
                        "description": "Pasted TurboScribe export with timestamps.",
                    },
                },
                "required": ["draft_id", "turboscribe_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browse_web",
            "description": (
                "Open a headless browser (saved profile) and return page text. "
                "Use for live web research, vidIQ, Trends, competitor pages."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Full URL or site alias: vidiq, youtube, trends, turboscribe.",
                    },
                    "screenshot": {
                        "type": "boolean",
                        "description": "Save screenshot to data/screenshots/",
                    },
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_browser",
            "description": (
                "Open a visible browser on Desktop for human login or manual steps. "
                "Aliases: vidiq, youtube, trends, turboscribe."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL or site alias."},
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "setup_youtube_channel",
            "description": (
                "Open a browser and set up a YouTube channel. Google phone/CAPTCHA "
                "requires a one-time human step — cannot be fully automated."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "channel_name": {"type": "string", "description": "YouTube channel display name."},
                    "use_existing_google_account": {
                        "type": "boolean",
                        "description": "True if Google account already exists; sign in manually once.",
                    },
                },
                "required": ["channel_name"],
            },
        },
    },
]


class ToolRunner:
    def __init__(
        self,
        store: MemoryStore,
        generator: DraftGenerator,
        queue: ApprovalQueue,
        router: CourseRouter | None = None,
    ) -> None:
        self.store = store
        self.generator = generator
        self.queue = queue
        self.router = router
        self._memory = MemoryExtensions(store)
        self._handlers: dict[str, Callable[[dict[str, Any]], str]] = {
            "create_draft": self._create_draft,
            "list_pending_drafts": self._list_pending_drafts,
            "show_draft": self._show_draft,
            "approve_draft": self._approve_draft,
            "reject_draft": self._reject_draft,
            "get_learned_feedback": self._get_learned_feedback,
            "get_stats": self._get_stats,
            "get_course_guidance": self._get_course_guidance,
            "list_free_tools": self._list_free_tools,
            "apply_channel_branding": self._apply_channel_branding,
            "prepare_video_production": self._prepare_video_production,
            "browse_web": self._browse_web,
            "open_browser": self._open_browser,
            "setup_youtube_channel": self._setup_youtube_channel,
            "get_channel_brand": self._get_channel_brand,
            "queue_dev_task": self._queue_dev_task,
            "list_pending_improvements": self._list_pending_improvements,
            "sync_youtube_analytics": self._sync_youtube_analytics,
            "get_youtube_status": self._get_youtube_status,
            "mark_channel_ready": self._mark_channel_ready,
            "score_video_performance": self._score_video_performance,
        }

    def run(self, name: str, arguments: dict[str, Any]) -> str:
        handler = self._handlers.get(name)
        if handler is None:
            return json.dumps({"error": f"Unknown tool: {name}"})
        try:
            return handler(arguments)
        except Exception as exc:  # noqa: BLE001 - surface tool errors to the model
            return json.dumps({"error": str(exc)})

    def _create_draft(self, args: dict[str, Any]) -> str:
        from shorts_bot.production.research import deep_research_topic

        topic = args["topic"]
        research = deep_research_topic(topic)
        draft = self.generator.create_and_store(topic, args.get("angle"), research=research)
        return json.dumps(
            {
                "draft_id": draft.id,
                "status": draft.status,
                "topic": draft.topic,
                "hook": draft.hook,
                "help_angle": draft.help_angle,
                "quality_notes": draft.quality_notes,
                "message": "Draft created and waiting for your approval.",
            }
        )

    def _list_pending_drafts(self, _args: dict[str, Any]) -> str:
        drafts = self.queue.pending()
        payload = [
            {
                "draft_id": d.id,
                "topic": d.topic,
                "hook": d.hook,
                "help_angle": d.help_angle,
                "quality_notes": d.quality_notes,
            }
            for d in drafts
        ]
        return json.dumps({"pending": payload, "count": len(payload)})

    def _show_draft(self, args: dict[str, Any]) -> str:
        draft = self.store.get_draft(int(args["draft_id"]))
        return json.dumps(
            {
                "draft_id": draft.id,
                "status": draft.status,
                "topic": draft.topic,
                "hook": draft.hook,
                "help_angle": draft.help_angle,
                "script": draft.script,
                "quality_notes": draft.quality_notes,
                "review_note": draft.review_note,
            }
        )

    def _approve_draft(self, args: dict[str, Any]) -> str:
        from shorts_bot.learning.feedback import learn_from_draft

        draft = self.queue.approve(int(args["draft_id"]), args.get("note", ""))
        learned = learn_from_draft(self._memory, draft.topic, args.get("note", ""), "approved")
        return json.dumps(
            {
                "draft_id": draft.id,
                "status": draft.status,
                "message": f"Draft approved. {learned}",
            }
        )

    def _reject_draft(self, args: dict[str, Any]) -> str:
        from shorts_bot.learning.feedback import learn_from_draft

        draft = self.queue.reject(int(args["draft_id"]), args["reason"])
        learned = learn_from_draft(self._memory, draft.topic, args["reason"], "rejected")
        return json.dumps(
            {
                "draft_id": draft.id,
                "status": draft.status,
                "message": f"Draft rejected. {learned}",
            }
        )

    def _get_learned_feedback(self, _args: dict[str, Any]) -> str:
        return json.dumps({"feedback": self.store.learned_patterns(limit=15)})

    def _get_stats(self, _args: dict[str, Any]) -> str:
        return json.dumps(self.store.stats())

    def _get_course_guidance(self, args: dict[str, Any]) -> str:
        if self.router is None:
            return json.dumps({"error": "Course router not loaded"})
        query = args.get("query", "")
        route = self.router.route(query)
        return json.dumps(
            {
                "main_lever": route.main_lever,
                "files": route.files,
                "combination": route.combination_note,
                "guidance": self.router.build_guidance(query),
            }
        )

    def _list_free_tools(self, _args: dict[str, Any]) -> str:
        if self.router is None:
            return json.dumps({"error": "Course not loaded"})
        return json.dumps({"free_services": self.router.kb.free_services})

    def _score_video_performance(self, args: dict[str, Any]) -> str:
        from shorts_bot.learning.score_helpers import propose_reward_improvement
        metrics = {k: v for k, v in args.items() if k != "video_label" and v is not None}
        engine = RewardEngine(self._memory)
        result = engine.score(args["video_label"], metrics)
        proposer = ImprovementProposer(self._memory, client=None)
        imp = propose_reward_improvement(self._memory, proposer, result)
        payload: dict[str, Any] = {
            "score": result.score,
            "verdict": result.verdict,
            "reason": result.reason,
            "diagnosis": result.diagnosis,
        }
        if imp:
            payload["improvement"] = {"id": imp.id, "title": imp.title, "pros": imp.pros, "cons": imp.cons}
        return json.dumps(payload)

    def _get_channel_brand(self, _args: dict[str, Any]) -> str:
        from pathlib import Path

        from shorts_bot.brand.loader import ChannelBrand

        brand = ChannelBrand()
        niches = ""
        niche_path = Path("docs/CHANNEL_NICHES.md")
        if niche_path.exists():
            niches = niche_path.read_text(encoding="utf-8")[:2000]
        return json.dumps(
            {
                "identity": brand.identity_summary()[:1500],
                "voice": brand.voice()[:1000],
                "youtube_copy": brand.youtube_copy(),
                "niches": niches,
            }
        )

    def _queue_dev_task(self, args: dict[str, Any]) -> str:
        task = self._memory.create_dev_task(
            title=args["title"],
            description=args["description"],
            source="agent",
        )
        return json.dumps(
            {
                "id": task.id,
                "title": task.title,
                "message": "Dev task queued — human must approve in web UI.",
            }
        )

    def _list_pending_improvements(self, _args: dict[str, Any]) -> str:
        pending = self._memory.list_improvements(status="pending")
        payload = [
            {
                "id": i.id,
                "title": i.title,
                "category": i.category,
                "description": i.description,
                "pros": i.pros,
                "cons": i.cons,
            }
            for i in pending
        ]
        return json.dumps({"pending": payload, "count": len(payload)})

    def _sync_youtube_analytics(self, _args: dict[str, Any]) -> str:
        from shorts_bot.training.proposer import ImprovementProposer
        from shorts_bot.youtube.sync import AnalyticsSync

        sync = AnalyticsSync(self._memory, ImprovementProposer(self._memory, client=None))
        result = sync.run()
        return json.dumps(
            {
                "ok": result.ok,
                "message": result.message,
                "videos_scored": result.videos_scored,
                "improvements_created": result.improvements_created,
                "rewards": result.rewards or [],
            }
        )

    def _get_youtube_status(self, _args: dict[str, Any]) -> str:
        saved = self.store.channel_summary()
        try:
            live = check_studio(settings.browser_profile_dir, headless=True)
            return json.dumps(
                {
                    "saved": saved,
                    "live": {
                        "logged_in": live.logged_in,
                        "in_studio": live.in_studio,
                        "channel_name": live.channel_name,
                        "message": live.message,
                        "url": live.url,
                    },
                }
            )
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"saved": saved, "live_error": str(exc)})

    def _mark_channel_ready(self, args: dict[str, Any]) -> str:
        name = args.get("channel_name")
        note = args.get("note", "Human finished channel setup.")
        self.store.mark_channel_ready(channel_name=name, note=note)
        return json.dumps({"message": "Channel marked ready.", "channel_name": name, "note": note})

    def _prepare_video_production(self, args: dict[str, Any]) -> str:
        from shorts_bot.production.pack import build_production_pack

        try:
            pack = build_production_pack(
                self.store,
                draft_id=int(args["draft_id"]),
                turboscribe_text=args["turboscribe_text"],
            )
        except (ValueError, KeyError) as exc:
            return json.dumps({"ok": False, "message": str(exc)})
        return json.dumps(
            {
                "ok": True,
                "message": pack.message,
                "draft_id": pack.draft_id,
                "topic": pack.topic,
                "image_count": pack.image_count,
                "output_dir": str(pack.output_dir),
                "manifest": str(pack.manifest_path),
            }
        )

    def _apply_channel_branding(self, args: dict[str, Any]) -> str:
        operator = YouTubeChannelBranding(
            profile_dir=settings.browser_profile_dir,
            headless=False,
        )
        use_brand = args.get("use_brand_file", True)
        name = args.get("channel_name")
        desc = args.get("description")
        if use_brand and not name and not desc:
            result = operator.apply_from_brand_file()
        else:
            result = operator.apply(channel_name=name, description=desc)
        return json.dumps(
            {
                "status": result.status,
                "message": result.message,
                "name_updated": result.name_updated,
                "description_updated": result.description_updated,
                "channel_name": result.channel_name,
                "screenshot": result.screenshot_path,
                "url": result.current_url,
            }
        )

    def _browse_web(self, args: dict[str, Any]) -> str:
        from shorts_bot.browser.session import browse_url

        try:
            result = browse_url(
                args["url"],
                screenshot=bool(args.get("screenshot", False)),
            )
            return json.dumps(
                {
                    "ok": True,
                    "url": result.url,
                    "title": result.title,
                    "logged_in": result.logged_in_hint,
                    "text": result.text[:6000],
                    "screenshot": result.screenshot_path,
                    "message": result.summary()[:4000],
                }
            )
        except Exception as exc:
            return json.dumps({"ok": False, "message": str(exc)})

    def _open_browser(self, args: dict[str, Any]) -> str:
        from shorts_bot.browser.session import open_browser_for_human

        try:
            result = open_browser_for_human(args["url"])
            return json.dumps(
                {
                    "ok": True,
                    "url": result.url,
                    "message": result.message or result.summary(),
                }
            )
        except Exception as exc:
            return json.dumps({"ok": False, "message": str(exc)})

    def _setup_youtube_channel(self, args: dict[str, Any]) -> str:
        channel_name = args.get("channel_name") or settings.youtube_channel_name
        operator = YouTubeChannelSetup(
            profile_dir=settings.browser_profile_dir,
            headless=False,
        )
        result = operator.run_with_unique_name(
            base_name=channel_name,
            use_existing_google_account=bool(args.get("use_existing_google_account", False)),
        )
        return json.dumps(
            {
                "status": result.status,
                "message": result.message,
                "screenshot": result.screenshot_path,
                "url": result.current_url,
            }
        )
