"""Chief Manager — delegates to specialists, optional timed work sessions."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from shorts_bot.agents.duration import (
    ParsedDuration,
    clamp_work_seconds,
    format_duration,
    parse_work_duration,
)
from shorts_bot.agents.roles import CHIEF_MANAGER
from shorts_bot.agents.runner import SpecialistRunner
from shorts_bot.agents.work_loop import WorkSession, run_timed_work
from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore

log = logging.getLogger(__name__)

ProgressCallback = Callable[[str], None]

MANAGER_PREFIXES = ("manager:", "chief:", "@manager ")


@dataclass
class ManagerResult:
    reply: str
    parsed: ParsedDuration
    work_seconds: int
    session: WorkSession | None = None
    used_manager: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "reply": self.reply,
            "work_seconds": self.work_seconds,
            "had_work_budget": self.parsed.has_work_budget,
            "tasks_completed": len(self.session.log) if self.session else 0,
            "work_log": self.session.work_log_dicts() if self.session else [],
            "elapsed_seconds": int(self.session.elapsed) if self.session else 0,
        }


def strip_manager_prefix(message: str) -> str:
    text = message.strip()
    lower = text.lower()
    for prefix in MANAGER_PREFIXES:
        if lower.startswith(prefix):
            return text[len(prefix) :].strip()
    return text


def should_use_manager(message: str) -> bool:
    """Route to chief manager when duration directive or explicit prefix."""
    if not settings.manager_enabled:
        return False
    text = strip_manager_prefix(message)
    lower = message.strip().lower()
    if any(lower.startswith(p) for p in MANAGER_PREFIXES):
        return True
    parsed = parse_work_duration(text)
    return parsed.has_work_budget


class ChiefManager:
    """Single interface for the human — runs workers behind the scenes."""

    def __init__(
        self,
        store: MemoryStore | None = None,
        *,
        runner: SpecialistRunner | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> None:
        self.store = store or MemoryStore(settings.database_path)
        self.runner = runner or SpecialistRunner()
        self.on_progress = on_progress or (lambda _m: None)

    def handle(self, message: str) -> ManagerResult:
        raw = message.strip()
        stripped = strip_manager_prefix(raw)
        parsed = parse_work_duration(stripped)

        work_seconds = 0
        session: WorkSession | None = None

        if parsed.has_work_budget:
            work_seconds = clamp_work_seconds(
                parsed.work_seconds or 0,
                minimum=settings.manager_work_floor_seconds,
                maximum=settings.manager_max_work_seconds,
            )
            self.on_progress(
                f"Work budget: {format_duration(work_seconds)} — starting specialist team…"
            )
            session = run_timed_work(
                parsed.cleaned_message or stripped,
                work_seconds,
                on_progress=self.on_progress,
            )
            self.on_progress(
                f"Work session done — {len(session.log)} tasks in {format_duration(int(session.elapsed))}."
            )

        reply = self._synthesize(parsed.cleaned_message or stripped, session)
        self.store.save_chat("user", raw)
        self.store.save_chat("assistant", reply)
        return ManagerResult(
            reply=reply,
            parsed=parsed,
            work_seconds=work_seconds,
            session=session,
        )

    def _synthesize(self, user_request: str, session: WorkSession | None) -> str:
        if not self.runner.available:
            return self._offline_reply(user_request, session)

        context = session.context_for_synthesis() if session else "No timed work session."
        task = f"User said:\n{user_request}\n\nWrite the final manager reply."

        synthesis = self.runner.run(
            CHIEF_MANAGER,
            task,
            context=context,
            temperature=CHIEF_MANAGER.temperature,
        )

        # Append structured footer for transparency
        footer_parts = []
        if session and session.log:
            footer_parts.append(
                f"\n\n---\n**Work session:** {len(session.log)} tasks · "
                f"{format_duration(int(session.elapsed))} / "
                f"{format_duration(session.budget_seconds)} budget"
            )
            for entry in session.log:
                line = f"• {entry.summary}"
                if entry.artifacts.get("draft_id"):
                    line += f" → draft #{entry.artifacts['draft_id']}"
                footer_parts.append(line)
            footer_parts.append("Say `pending` to review drafts.")

        return synthesis + "".join(footer_parts)

    def _offline_reply(self, user_request: str, session: WorkSession | None) -> str:
        lines = [
            "Chief Manager (offline — set GEMINI_API_KEY).",
            f"Request: {user_request}",
        ]
        if session:
            lines.append(f"Completed {len(session.log)} tasks:")
            for e in session.log:
                lines.append(f"- {e.summary}")
                if e.artifacts.get("draft_id"):
                    lines.append(f"  draft #{e.artifacts['draft_id']}")
        else:
            lines.append("No work budget detected. Try: take 30 minutes to plan cosy shorts")
        return "\n".join(lines)


def run_manager_job(
    message: str,
    work_seconds: int,
    *,
    on_progress: ProgressCallback | None = None,
) -> ManagerResult:
    """Entry for background jobs — forces a work budget even if not parsed from text."""
    mgr = ChiefManager(on_progress=on_progress)
    parsed = parse_work_duration(strip_manager_prefix(message))
    budget = work_seconds or parsed.work_seconds or 0
    if budget > 0:
        budget = clamp_work_seconds(
            budget,
            minimum=settings.manager_work_floor_seconds,
            maximum=settings.manager_max_work_seconds,
        )
        session = run_timed_work(
            parsed.cleaned_message or message,
            budget,
            on_progress=on_progress or (lambda _m: None),
        )
        reply = mgr._synthesize(parsed.cleaned_message or message, session)
        mgr.store.save_chat("user", message)
        mgr.store.save_chat("assistant", reply)
        return ManagerResult(
            reply=reply,
            parsed=parsed,
            work_seconds=budget,
            session=session,
        )
    return mgr.handle(message)
