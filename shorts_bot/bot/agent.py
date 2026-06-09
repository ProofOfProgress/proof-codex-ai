from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from shorts_bot.bot.tools import TOOL_SCHEMAS, ToolRunner
from shorts_bot.config import settings
from shorts_bot.course.loader import CourseKnowledgeBase
from shorts_bot.course.router import CourseRouter
from shorts_bot.memory.store import MemoryStore

RESPONSE_FORMAT = """
Every substantive answer must follow this structure:
1. Main decision — which lever (idea, hook, visuals, retention, payoff, etc.)
2. Action plan — practical steps from the course checklists
3. Jenny-approved constraint check — confirm non-negotiables are respected
4. Uniqueness space — what can be customized without breaking hook → momentum → payoff

Channel constraints:
- Faceless Shorts only (9:16). No slop. Must genuinely help people.
- Niche TBD — infer the most useful version and proceed.
- Approve before posting. Production uses free-first stack: CapCut, YouTube Audio Library, Canva free, Google Drive.
- YouTube channel exists — human configured name/handle. Use get_youtube_status to confirm.
- Do not ask clarifying questions unless truly impossible to proceed.
"""


def build_system_prompt(kb: CourseKnowledgeBase) -> str:
    router = kb.router_prompt.strip()
    free = kb.free_services.strip()
    return f"""{router}

{RESPONSE_FORMAT}

FREE-FIRST TOOL STACK (from course):
{free[:2000]}

You are also the Shorts Bot operator. Use tools to create drafts, manage approvals, and learn from feedback.
When the human wants a draft, use create_draft. When they approve or reject, use the matching tools.
Sound like a smart strategist, not a rigid router. Do not mention file numbers unless asked."""


class ShortsBotAgent:
    def __init__(
        self,
        store: MemoryStore,
        tool_runner: ToolRunner,
        client: OpenAI | None,
        router: CourseRouter,
        kb: CourseKnowledgeBase,
    ) -> None:
        self.store = store
        self.tool_runner = tool_runner
        self.client = client
        self.router = router
        self.kb = kb
        self.messages: list[dict[str, Any]] = [
            {"role": "system", "content": build_system_prompt(kb)}
        ]

    def chat(self, user_message: str) -> str:
        self.store.save_chat("user", user_message)
        guidance = self.router.build_guidance(user_message)
        augmented = (
            f"{user_message}\n\n"
            f"[JENNY COURSE CONTEXT — use ONLY this + tools, no outside advice]\n"
            f"{guidance}"
        )
        self.messages.append({"role": "user", "content": augmented})

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
                "- pending / show <id> / approve / reject\n"
                "- stats / feedback\n"
                "- course <question>  (Jenny course routing)\n"
                "- free tools\n"
                "- setup channel <name>  (opens browser for YouTube — you may need phone code once)\n"
                "Set OPENAI_API_KEY for full Jenny strategist mode."
            )
        if text.startswith("setup channel "):
            name = user_message[14:].strip()
            data = json.loads(
                self.tool_runner.run("setup_youtube_channel", {"channel_name": name})
            )
            return data.get("message", str(data))
        if text == "free tools":
            return self.kb.free_services or "No free services doc found."
        if text.startswith("course "):
            query = user_message[7:].strip()
            route = self.router.route(query)
            return (
                f"Main lever: {route.main_lever}\n"
                f"Files: {', '.join(route.files)}\n\n"
                f"{self.router.build_guidance(query)[:3000]}"
            )
        if text.startswith("draft "):
            topic = user_message[6:].strip()
            result = self.tool_runner.run("create_draft", {"topic": topic})
            data = json.loads(result)
            route = self.router.route(topic)
            return (
                f"Created draft #{data['draft_id']} about '{data['topic']}'.\n"
                f"Lever: {route.main_lever}\n"
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

        route = self.router.route(user_message)
        return (
            f"Offline mode. Routed lever: {route.main_lever} (files {', '.join(route.files)}).\n"
            "Type 'course <your question>' for course guidance, or set OPENAI_API_KEY for full chat."
        )
