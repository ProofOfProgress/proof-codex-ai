"""Base underling — internal workers; humans never chat with these directly."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from shorts_bot.agents.roles import AgentRole
from shorts_bot.agents.runner import SpecialistRunner
from shorts_bot.config import settings

log = logging.getLogger(__name__)

ProgressCallback = Callable[[str], None]

UNDERLING_LOG_DIR = Path("data/underlings")


@dataclass
class UnderlingResult:
    """Output from one underling task — consumed by Chief Manager only."""

    underling: str
    task: str
    summary: str
    detail: str
    elapsed_seconds: float
    artifacts: dict[str, Any] = field(default_factory=dict)

    def to_work_log_entry(self) -> dict[str, Any]:
        from shorts_bot.agents.tasks import WorkLogEntry

        return WorkLogEntry(
            task=self.task,
            role=self.underling,
            summary=self.summary,
            elapsed_seconds=self.elapsed_seconds,
            detail=self.detail,
            artifacts=self.artifacts,
        )


def append_underling_log(line: str) -> None:
    """Internal audit trail — not shown to user as a chat interface."""
    UNDERLING_LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = UNDERLING_LOG_DIR / "work.log"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {line}\n")


class Underling(ABC):
    """Specialist worker — only the Chief Manager (or Research Lead) dispatches these."""

    role: AgentRole
    name: str

    def __init__(
        self,
        runner: SpecialistRunner,
        *,
        on_progress: ProgressCallback | None = None,
    ) -> None:
        self.runner = runner
        self.on_progress = on_progress or (lambda _m: None)

    def _progress(self, msg: str) -> None:
        self.on_progress(f"[{self.name}] {msg}")
        append_underling_log(f"{self.name}: {msg}")

    @abstractmethod
    def execute(self, task: str, *, context: str = "") -> UnderlingResult:
        ...

    def _gemini(self, task: str, *, context: str = "") -> str:
        return self.runner.run(self.role, task, context=context)
