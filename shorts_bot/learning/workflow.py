"""Versioned daily-loop workflows — steps + params the bot can evolve over time."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from shorts_bot.config import settings

WORKFLOW_STATE_KEY = "workflow:daily_invideo:active"
DEFAULT_WORKFLOW_PATH = Path("data/workflows/daily_invideo_v1.json")

from shorts_bot.production.hooks import HOOK_TEMPLATES


@dataclass
class WorkflowStep:
    id: str
    enabled: bool = True
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "enabled": self.enabled, "params": dict(self.params)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowStep:
        return cls(
            id=str(data["id"]),
            enabled=bool(data.get("enabled", True)),
            params=dict(data.get("params") or {}),
        )


@dataclass
class WorkflowDefinition:
    id: str
    version: int
    steps: list[WorkflowStep]
    description: str = ""

    def step(self, step_id: str) -> WorkflowStep | None:
        for s in self.steps:
            if s.id == step_id:
                return s
        return None

    def enabled_steps(self) -> list[WorkflowStep]:
        return [s for s in self.steps if s.enabled]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowDefinition:
        return cls(
            id=str(data["id"]),
            version=int(data.get("version", 1)),
            description=str(data.get("description") or ""),
            steps=[WorkflowStep.from_dict(s) for s in data.get("steps") or []],
        )


@dataclass
class StepResult:
    step_id: str
    ok: bool
    detail: str = ""
    duration_sec: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "ok": self.ok,
            "detail": self.detail[:500],
            "duration_sec": round(self.duration_sec, 2),
        }


@dataclass
class WorkflowRun:
    workflow_id: str
    workflow_version: int
    draft_id: int | None
    topic: str
    ok: bool
    step_results: list[StepResult]
    mutation_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "workflow_version": self.workflow_version,
            "draft_id": self.draft_id,
            "topic": self.topic,
            "ok": self.ok,
            "step_results": [s.to_dict() for s in self.step_results],
            "mutation_notes": self.mutation_notes,
        }


def load_seed_workflow(path: Path | None = None) -> WorkflowDefinition:
    p = path or DEFAULT_WORKFLOW_PATH
    data = json.loads(p.read_text(encoding="utf-8"))
    return WorkflowDefinition.from_dict(data)


def load_active_workflow(store) -> WorkflowDefinition:
    """Active workflow from DB, else seed file."""
    from shorts_bot.memory.store import MemoryStore

    if not isinstance(store, MemoryStore):
        store = store.store  # MemoryExtensions
    raw = store.get_channel_state(WORKFLOW_STATE_KEY)
    if raw:
        try:
            return WorkflowDefinition.from_dict(json.loads(raw))
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    wf = load_seed_workflow()
    save_active_workflow(store, wf)
    return wf


def save_active_workflow(store, workflow: WorkflowDefinition) -> None:
    from shorts_bot.memory.store import MemoryStore

    if not isinstance(store, MemoryStore):
        store = store.store
    store.set_channel_state(WORKFLOW_STATE_KEY, json.dumps(workflow.to_dict()))


def bump_workflow_version(workflow: WorkflowDefinition, *, note: str = "") -> WorkflowDefinition:
    """Immutable-style version bump after a mutation."""
    data = workflow.to_dict()
    data["version"] = int(workflow.version) + 1
    if note:
        data["description"] = f"{workflow.description} | v{data['version']}: {note}".strip(" |")
    return WorkflowDefinition.from_dict(data)


def set_step_param(
    workflow: WorkflowDefinition,
    step_id: str,
    key: str,
    value: Any,
) -> WorkflowDefinition:
    updated = deepcopy(workflow)
    step = updated.step(step_id)
    if step is None:
        return workflow
    step.params[key] = value
    return updated
