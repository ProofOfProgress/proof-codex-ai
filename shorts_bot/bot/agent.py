from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from shorts_bot.bot.tools import TOOL_SCHEMAS, ToolRunner
from shorts_bot.config import settings
from shorts_bot.codex import CODEX_NAME
from shorts_bot.course.loader import CourseKnowledgeBase
from shorts_bot.course.router import CourseRouter
from shorts_bot.brand.loader import ChannelBrand
from shorts_bot.memory.agent_memory import AgentMemoryStore
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore

RESPONSE_FORMAT = """
Every substantive answer must follow this structure:
1. Main decision — which lever (idea, hook, visuals, retention, payoff, etc.)
2. Action plan — practical steps from the course checklists
3. Jenny-approved constraint check — confirm non-negotiables are respected
4. Uniqueness space — what can be customized without breaking hook → momentum → payoff

Channel: **Don't Blink** — real faceless creator voice (Jenny Hoyos). Same struggles as viewer; share what helped YOU. First person. Subtitles + AI horror motions act out advice.
Channel constraints:
- Jenny: hook→momentum→payoff, mute-safe visuals, singular you, start ASAP.
- Faceless Shorts (9:16). No slop. One concrete action per Short.
- Niche: sleep, focus, boundaries, calm.
- Approve before posting. Free-first: CapCut, YouTube Audio Library, Canva.
- YouTube channel exists — human configured name/handle. Use get_youtube_status to confirm.
- Do not ask clarifying questions unless truly impossible to proceed.
"""


def build_system_prompt(
    kb: CourseKnowledgeBase,
    brand: ChannelBrand | None = None,
    *,
    memory_block: str = "",
    learning_block: str = "",
) -> str:
    router = kb.router_prompt.strip()
    free = kb.free_services.strip()
    brand_block = brand.draft_instructions() if brand else ""
    memory_section = f"\n\n{memory_block}\n" if memory_block else ""
    learning_section = f"\n\n{learning_block}\n" if learning_block else ""
    return f"""{router}

KNOWLEDGE BASE: **{CODEX_NAME}** (course/files 01–09 + verbatim). Route every answer through Codex — no outside creator folklore.

{RESPONSE_FORMAT}
{memory_section}{learning_section}
CHANNEL BRAND (voice + positioning):
{brand_block[:2200]}

FREE-FIRST TOOL STACK (from course):
{free[:2000]}

You are the Don't Blink operator — helpful first, uncanny second (barely). Use tools for drafts and approvals.
Sound like a calm strategist who knows too much but only uses it to help. Do not mention file numbers unless asked.
When the user says remember / operating rule / don't forget, acknowledge and use the remember_memory tool if available.
You CAN run web browsers: use browse_web for headless research pages, open_browser for human login on Desktop (vidiq, youtube, trends)."""


class ShortsBotAgent:
    def __init__(
        self,
        store: MemoryStore,
        tool_runner: ToolRunner,
        client: OpenAI | None,
        router: CourseRouter,
        kb: CourseKnowledgeBase,
        brand: ChannelBrand | None = None,
        agent_memory: AgentMemoryStore | None = None,
        training_memory: MemoryExtensions | None = None,
        *,
        llm_model: str | None = None,
        llm_provider: str = "offline",
    ) -> None:
        self.store = store
        self.tool_runner = tool_runner
        self.client = client
        self.llm_model = llm_model or settings.openai_model
        self.llm_provider = llm_provider
        self.router = router
        self.kb = kb
        self.brand = brand or ChannelBrand()
        self.agent_memory = agent_memory
        self.training_memory = training_memory
        memory_block = agent_memory.context_block() if agent_memory else ""
        learning_block = training_memory.applied_training_context() if training_memory else ""
        self.messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": build_system_prompt(
                    kb,
                    self.brand,
                    memory_block=memory_block,
                    learning_block=learning_block,
                ),
            }
        ]
        for msg in store.recent_chat(settings.memory_chat_context_limit):
            if msg["role"] in ("user", "assistant") and msg.get("content"):
                self.messages.append({"role": msg["role"], "content": msg["content"]})

    def _refresh_system_prompt(self) -> None:
        memory_block = self.agent_memory.context_block() if self.agent_memory else ""
        learning_block = self.training_memory.applied_training_context() if self.training_memory else ""
        self.messages[0] = {
            "role": "system",
            "content": build_system_prompt(
                self.kb,
                self.brand,
                memory_block=memory_block,
                learning_block=learning_block,
            ),
        }

    def chat(self, user_message: str) -> str:
        self._refresh_system_prompt()
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
            try:
                response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=self.messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=0.7,
                )
            except Exception:
                reply = self._offline_reply(user_message)
                self.messages.append({"role": "assistant", "content": reply})
                self.store.save_chat("assistant", reply)
                return reply
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
                "Offline mode (no GEMINI_API_KEY or OPENAI_API_KEY).\n"
                "Commands:\n"
                "- draft <topic>\n"
                "- pending / show <id> / approve / reject\n"
                "- stats / feedback\n"
                "- remember <fact> / memory / forget <id>\n"
                "- browse <url> / browser open vidiq\n"
                "- course <question>  (Jenny course routing)\n"
                "- free tools\n"
                "- setup channel <name>  (opens browser for YouTube — you may need phone code once)\n"
                "- apply brand  (updates channel name + description in Studio from youtube_copy.txt)\n"
                "- produce <id> | <turboscribe paste>  (still-image video pack for CapCut)\n"
                "Set GEMINI_API_KEY (free) or OPENAI_API_KEY for full Jenny strategist mode."
            )
        from shorts_bot.memory.agent_memory import (
            is_memory_list_request,
            parse_forget_request,
            parse_remember_request,
        )

        if is_memory_list_request(text):
            return self.agent_memory.format_list() if self.agent_memory else "No memory store."
        forget_id = parse_forget_request(text)
        if forget_id is not None and self.agent_memory:
            ok = self.agent_memory.delete_memory(forget_id)
            return f"Forgot memory #{forget_id}." if ok else f"No memory #{forget_id}."
        remembered = parse_remember_request(text)
        if remembered is not None and self.agent_memory:
            category, content = remembered
            mem = self.agent_memory.add_memory(content=content, category=category, source="user")
            return f"Saved memory #{mem.id}: {mem.content}"
        if text.startswith("setup channel "):
            name = user_message[14:].strip()
            data = json.loads(
                self.tool_runner.run("setup_youtube_channel", {"channel_name": name})
            )
            return data.get("message", str(data))
        if text in {"apply brand", "apply branding", "channel brand", "update channel"}:
            data = json.loads(self.tool_runner.run("apply_channel_branding", {}))
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
        if text in {"improvements", "pending improvements"}:
            result = json.loads(self.tool_runner.run("list_pending_improvements", {}))
            pending = result.get("pending", [])
            if not pending:
                return "No pending improvements."
            return "Pending improvements:\n" + "\n".join(
                f"#{p['id']} [{p['category']}] {p['title']}" for p in pending
            )

        route = self.router.route(user_message)
        return (
            f"Offline mode. Routed lever: {route.main_lever} (files {', '.join(route.files)}).\n"
            "Type 'course <your question>' for course guidance, or set GEMINI_API_KEY for full chat."
        )
