"""Run Gemini specialist agents (one role, one task)."""

from __future__ import annotations

import json
import logging
from typing import Any

from shorts_bot.agents.roles import AgentRole
from shorts_bot.llm.provider import get_llm_backend

log = logging.getLogger(__name__)


class SpecialistRunner:
    """Thin wrapper around get_llm_backend() for role-based calls."""

    def __init__(self) -> None:
        self._backend = get_llm_backend()

    @property
    def available(self) -> bool:
        return self._backend is not None

    def run(
        self,
        role: AgentRole,
        task: str,
        *,
        context: str = "",
        temperature: float | None = None,
    ) -> str:
        if not self._backend:
            return f"[offline] {role.name}: set GEMINI_API_KEY to run specialists."

        user_parts = []
        if context.strip():
            user_parts.append(f"CONTEXT:\n{context.strip()}")
        user_parts.append(f"TASK:\n{task.strip()}")
        user_content = "\n\n".join(user_parts)

        try:
            response = self._backend.client.chat.completions.create(
                model=self._backend.model,
                messages=[
                    {"role": "system", "content": role.system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=temperature if temperature is not None else role.temperature,
            )
            return (response.choices[0].message.content or "").strip() or "(empty response)"
        except Exception as exc:
            log.warning("Specialist %s failed: %s", role.name, exc)
            return f"[error] {role.name}: {exc}"

    def run_json(
        self,
        role: AgentRole,
        task: str,
        *,
        context: str = "",
    ) -> dict[str, Any]:
        raw = self.run(
            role,
            task + "\n\nReturn valid JSON only.",
            context=context,
            temperature=0.3,
        )
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # try to extract JSON block
            start = raw.find("{")
            end = raw.rfind("}")
            if start >= 0 and end > start:
                try:
                    return json.loads(raw[start : end + 1])
                except json.JSONDecodeError:
                    pass
            return {"raw": raw, "parse_error": True}
