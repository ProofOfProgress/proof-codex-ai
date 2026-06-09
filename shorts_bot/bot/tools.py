from __future__ import annotations

import json
from typing import Any, Callable

from shorts_bot.approval.queue import ApprovalQueue
from shorts_bot.config import settings
from shorts_bot.course.router import CourseRouter
from shorts_bot.drafts.generator import DraftGenerator
from shorts_bot.memory.store import MemoryStore
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
            "setup_youtube_channel": self._setup_youtube_channel,
            "get_youtube_status": self._get_youtube_status,
            "mark_channel_ready": self._mark_channel_ready,
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
        draft = self.generator.create_and_store(args["topic"], args.get("angle"))
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
        draft = self.queue.approve(int(args["draft_id"]), args.get("note", ""))
        return json.dumps(
            {
                "draft_id": draft.id,
                "status": draft.status,
                "message": "Draft approved. Video production comes later.",
            }
        )

    def _reject_draft(self, args: dict[str, Any]) -> str:
        draft = self.queue.reject(int(args["draft_id"]), args["reason"])
        return json.dumps(
            {
                "draft_id": draft.id,
                "status": draft.status,
                "message": "Draft rejected. I'll learn from your reason next time.",
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
