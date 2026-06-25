"""Daily autopilot — product topic → InVideo → MP4 → YouTube (evolvable workflow)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.learning.workflow_runner import DailyWorkflowResult, run_daily_invideo_workflow
from shorts_bot.memory.store import MemoryStore


@dataclass
class InVideoDailyResult:
    ok: bool
    draft_id: int
    topic: str
    project_url: str
    video_path: Path | None
    upload_url: str | None
    messages: list[str]
    workflow_version: int = 1
    evolution_summary: str = ""

    @property
    def summary(self) -> str:
        return "\n".join(self.messages)


def run_invideo_daily(
    *,
    topic: str | None = None,
    upload: bool | None = None,
    wait_render_sec: int = 2400,
) -> InVideoDailyResult:
    """
    One daily Short via InVideo (soul of the channel):
    pick product → brief → MCP project → browser generate/download → YouTube upload.

    Steps and params come from the active workflow (see workflow_cli status).
    """
    store = MemoryStore(settings.database_path)
    result: DailyWorkflowResult = run_daily_invideo_workflow(
        store,
        topic=topic,
        upload=upload,
        wait_render_sec=wait_render_sec,
    )
    return InVideoDailyResult(
        ok=result.ok,
        draft_id=result.draft_id,
        topic=result.topic,
        project_url=result.project_url,
        video_path=result.video_path,
        upload_url=result.upload_url,
        messages=result.messages,
        workflow_version=result.workflow_run.workflow_version,
        evolution_summary=result.evolution_summary,
    )
