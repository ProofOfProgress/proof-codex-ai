"""Retired jumpscare timing — stubs for upload_meta / pack_health imports."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class JumpscarePlan:
    has_jumpscare: bool = False
    scare_sentence_index: int = -1
    volume_warning: str = ""
    setup_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "has_jumpscare": self.has_jumpscare,
            "scare_sentence_index": self.scare_sentence_index,
            "volume_warning": self.volume_warning,
            "setup_seconds": self.setup_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JumpscarePlan:
        return cls(
            has_jumpscare=bool(data.get("has_jumpscare")),
            scare_sentence_index=int(data.get("scare_sentence_index") or data.get("primary_segment_index") or -1),
            volume_warning=str(data.get("volume_warning") or ""),
            setup_seconds=float(data.get("setup_seconds") or 0.0),
        )


def plan_for_draft(draft_id: int, sentence_count: int = 8) -> JumpscarePlan:
    return JumpscarePlan()


def load_plan_for_draft(draft_id: int, sentence_count: int = 8) -> JumpscarePlan:
    return JumpscarePlan()


def persist_plan(pack_dir, plan: JumpscarePlan) -> None:
    pass


def scare_sentence_indices(plan: JumpscarePlan) -> list[int]:
    return []


def sting_start_seconds(plan: JumpscarePlan) -> float:
    return 0.0
