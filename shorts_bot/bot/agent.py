from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from shorts_bot.bot.tools import TOOL_SCHEMAS, ToolRunner
from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore

AGENT_SYSTEM = """You are the Shorts Bot for a faceless YouTube Shorts channel.

Goals:
- Help the human operator ideate, draft, and review Shorts before anything gets posted.
- Content must genuinely help people. No slop, no filler, no empty engagement bait.
- Niche is still TBD. Propose useful ideas and ask clarifying questions when needed.
- Learn from approval/rejection feedback over time. There is no pre-built codex yet.
- Course material will be added later. For now, use conversation + feedback memory.

Workflow:
1. Discuss ideas with the human.
2. Create drafts when asked.
3. Show pending drafts and help approve/reject with clear reasons.
4. Approved drafts are not posted automatically yet — production (CapCut, video sites) comes later.

Be direct, practical, and concise. When creating drafts, use the create_draft tool.
When the human wants to approve or reject, use the appropriate tools."""


class ShortsBotAgent:
    def __init__(self, store: MemoryStore, tool_runner: ToolRunner, client: OpenAI | None) -> None:
        self.store = store
        self.tool_runner = tool_runner
        self.client = client
        self.messages: list[dict[str, Any]] = [{"role": "system", "content": AGENT_SYSTEM}]

    def chat(self, user_message: str) -> str:
        self.store.save_chat("user", user_message)
        self.messages.append({"role": "user", "content": user_message})

        if self.client is None:
            reply = self._offline_reply(user_message)
            self.messages.append({"role": "assistant", "content": reply})
            self.store.save_chat("assistant", reply)
            return reply

        for _ in range(6):
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=self.messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=0.7,
            )
            message = response.choices[0].message
            assistant_payload: dict[str, Any] = {"role": "assistant", "content": message.content or ""}
            if message.tool_calls:
                assistant_payload["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ]
            self.messages.append(assistant_payload)

            if not message.tool_calls:
                reply = (message.content or "").strip() or "Done."
                self.store.save_chat("assistant", reply)
                return reply

            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments or "{}")
                result = self.tool_runner.run(tool_call.function.name, args)
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

        reply = "I hit a tool loop limit. Try rephrasing."
        self.store.save_chat("assistant", reply)
        return reply

    def _offline_reply(self, user_message: str) -> str:
        text = user_message.strip().lower()
        if text in {"help", "/help"}:
            return (
                "Offline mode (no OPENAI_API_KEY).\n"
                "Commands:\n"
                "- draft <topic>\n"
                "- pending\n"
                "- show <id>\n"
                "- approve <id> [note]\n"
                "- reject <id> <reason>\n"
                "- stats\n"
                "- feedback\n"
                "Set OPENAI_API_KEY in .env for full conversational mode."
            )
        if text.startswith("draft "):
            topic = user_message[6:].strip()
            result = self.tool_runner.run("create_draft", {"topic": topic})
            data = json.loads(result)
            return (
                f"Created draft #{data['draft_id']} about '{data['topic']}'.\n"
                f"Hook: {data['hook']}\n"
                f"Help angle: {data['help_angle']}\n"
                f"Quality: {data['quality_notes']}\n"
                "Say 'pending' to review it."
            )
        if text == "pending":
            result = json.loads(self.tool_runner.run("list_pending_drafts", {}))
            if not result["pending"]:
                return "No pending drafts."
            lines = [f"#{d['draft_id']}: {d['topic']} — {d['hook']}" for d in result["pending"]]
            return "Pending drafts:\n" + "\n".join(lines)
        if text.startswith("show "):
            draft_id = int(text.split()[1])
            data = json.loads(self.tool_runner.run("show_draft", {"draft_id": draft_id}))
            return (
                f"Draft #{data['draft_id']} [{data['status']}]\n"
                f"Topic: {data['topic']}\n"
                f"Help: {data['help_angle']}\n"
                f"Hook: {data['hook']}\n"
                f"Script:\n{data['script']}\n"
                f"Quality: {data['quality_notes']}"
            )
        if text.startswith("approve "):
            parts = user_message.split(maxsplit=2)
            draft_id = int(parts[1])
            note = parts[2] if len(parts) > 2 else ""
            data = json.loads(self.tool_runner.run("approve_draft", {"draft_id": draft_id, "note": note}))
            return data["message"]
        if text.startswith("reject "):
            parts = user_message.split(maxsplit=2)
            if len(parts) < 3:
                return "Usage: reject <id> <reason>"
            data = json.loads(
                self.tool_runner.run(
                    "reject_draft",
                    {"draft_id": int(parts[1]), "reason": parts[2]},
                )
            )
            return data["message"]
        if text == "stats":
            data = json.loads(self.tool_runner.run("get_stats", {}))
            return f"Pending: {data['pending']}, Approved: {data['approved']}, Rejected: {data['rejected']}"
        if text == "feedback":
            data = json.loads(self.tool_runner.run("get_learned_feedback", {}))
            if not data["feedback"]:
                return "No feedback yet."
            lines = [f"[{f['decision']}] {f['topic']}: {f['reason']}" for f in data["feedback"]]
            return "Recent feedback:\n" + "\n".join(lines)

        return (
            "Offline mode. I understand basic commands (type 'help').\n"
            "Set OPENAI_API_KEY for natural conversation and smarter drafts."
        )
