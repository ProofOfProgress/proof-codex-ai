"""Legacy InVideo daily workflow — RETIRED."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shorts_bot.learning.workflow import WorkflowRun
from shorts_bot.memory.store import MemoryStore

_RETIRED_MSG = (
    "InVideo daily workflow is retired. Creative playbook: data/research/course/. "
    "Production: shorts_bot/tiktok_shop/ (Kling + Module 1 QC)."
)


@dataclass
class DailyWorkflowResult:
    ok: bool
    draft_id: int
    topic: str
    project_url: str
    video_path: Path | None
    upload_url: str | None
    messages: list[str]
    workflow_run: WorkflowRun | None
    evolution_summary: str

    @property
    def summary(self) -> str:
        return "\n".join(self.messages)


def run_daily_invideo_workflow(
    store: MemoryStore,
    *,
    topic: str | None = None,
    dry_run: bool = False,
) -> DailyWorkflowResult:
    raise RuntimeError(_RETIRED_MSG)
