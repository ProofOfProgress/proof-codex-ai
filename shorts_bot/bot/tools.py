from __future__ import annotations

import json
from typing import Any, Callable

from shorts_bot.approval.queue import ApprovalQueue
from shorts_bot.drafts.generator import DraftGenerator
from shorts_bot.memory.store import MemoryStore

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
]


class ToolRunner:
    def __init__(
        self,
        store: MemoryStore,
        generator: DraftGenerator,
        queue: ApprovalQueue,
    ) -> None:
        self.store = store
        self.generator = generator
        self.queue = queue
        self._handlers: dict[str, Callable[[dict[str, Any]], str]] = {
            "create_draft": self._create_draft,
            "list_pending_drafts": self._list_pending_drafts,
            "show_draft": self._show_draft,
            "approve_draft": self._approve_draft,
            "reject_draft": self._reject_draft,
            "get_learned_feedback": self._get_learned_feedback,
            "get_stats": self._get_stats,
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
