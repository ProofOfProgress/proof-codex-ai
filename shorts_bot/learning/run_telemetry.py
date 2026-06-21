"""Run telemetry — JSONL audit log for every workflow tick."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shorts_bot.config import settings
from shorts_bot.learning.workflow import WorkflowRun


def telemetry_path() -> Path:
    p = settings.data_dir / "telemetry" / "runs.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def record_run(
    run: WorkflowRun,
    *,
    extra: dict[str, Any] | None = None,
    evolution_summary: str = "",
) -> None:
    if not settings.run_telemetry_enabled:
        return
    row = {
        "at": datetime.now(timezone.utc).isoformat(),
        "workflow_id": run.workflow_id,
        "workflow_version": run.workflow_version,
        "draft_id": run.draft_id,
        "topic": run.topic,
        "ok": run.ok,
        "steps": [s.to_dict() for s in run.step_results],
        "mutation_notes": run.mutation_notes,
        "evolution_summary": evolution_summary,
    }
    if extra:
        row.update(extra)
    path = telemetry_path()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def recent_runs(limit: int = 20) -> list[dict]:
    path = telemetry_path()
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    out: list[dict] = []
    for line in lines[-limit:]:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return list(reversed(out))


def telemetry_summary() -> str:
    runs = recent_runs(limit=5)
    if not runs:
        return "No telemetry runs yet."
    lines = ["Recent runs:"]
    for r in runs:
        failed = next((s["step_id"] for s in r.get("steps", []) if not s.get("ok")), "—")
        lines.append(
            f"  {r.get('at', '')[:19]} draft={r.get('draft_id')} ok={r.get('ok')} fail={failed}"
        )
    return "\n".join(lines)
