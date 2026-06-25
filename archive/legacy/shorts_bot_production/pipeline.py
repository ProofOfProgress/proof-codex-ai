"""Production pipeline — InVideo only (legacy homemade render retired)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.legacy_retired import LegacyPipelineRetired


@dataclass
class PipelineResult:
    draft_id: int
    pack_dir: Path
    messages: list[str]
    video_path: Path | None
    upload_url: str | None
    report_path: Path | None = None
    step_timings: dict[str, float] = field(default_factory=dict)
    success: bool = True
    qc_passed: bool = True

    @property
    def ok(self) -> bool:
        return self.success


def finish_draft_pipeline(
    store: MemoryStore,
    draft_id: int,
    *,
    upload_youtube: bool | None = None,
    resume: bool = True,
) -> PipelineResult:
    """Finish a draft via InVideo backend."""
    backend = (getattr(settings, "pipeline_backend", None) or "invideo").strip().lower()
    if backend != "invideo":
        raise LegacyPipelineRetired(f"pipeline_backend={backend!r}")

    draft = store.get_draft(draft_id)
    from shorts_bot.invideo.script_pack import draft_pack_dir
    from shorts_bot.production.invideo_daily import run_invideo_daily

    result = run_invideo_daily(topic=draft.topic, upload=upload_youtube)
    pack = draft_pack_dir(draft_id)
    return PipelineResult(
        draft_id=draft_id,
        pack_dir=pack,
        messages=result.messages,
        video_path=result.video_path,
        upload_url=result.upload_url,
        success=result.ok,
        qc_passed=result.ok,
    )
