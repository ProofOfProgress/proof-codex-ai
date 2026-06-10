"""Idempotent pipeline checkpoints — skip completed steps on retry."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PIPELINE_STEPS = (
    "preflight",
    "humanize",
    "voiceover",
    "turboscribe",
    "pack",
    "render",
    "video_qc",
    "metadata",
    "upload",
)


@dataclass
class PipelineState:
    draft_id: int
    steps: dict[str, str] = field(default_factory=dict)
    updated_at: str = ""

    def path(self, pack_dir: Path) -> Path:
        return pack_dir / "pipeline_state.json"

    def is_done(self, step: str) -> bool:
        return self.steps.get(step) == "done"

    def mark(self, step: str, *, status: str = "done") -> None:
        self.steps[step] = status
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "draft_id": self.draft_id,
            "steps": self.steps,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> PipelineState:
        return cls(
            draft_id=int(data.get("draft_id", 0)),
            steps=dict(data.get("steps") or {}),
            updated_at=str(data.get("updated_at") or ""),
        )


def load_state(pack_dir: Path, draft_id: int) -> PipelineState:
    path = pack_dir / "pipeline_state.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return PipelineState.from_dict(data)
        except json.JSONDecodeError:
            pass
    return PipelineState(draft_id=draft_id)


def save_state(pack_dir: Path, state: PipelineState) -> None:
    pack_dir.mkdir(parents=True, exist_ok=True)
    state.path(pack_dir).write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")
