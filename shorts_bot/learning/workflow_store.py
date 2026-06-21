"""Persist workflow run history for evolution."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from shorts_bot.learning.workflow import WorkflowRun
from shorts_bot.memory.store import MemoryStore, _utc_now


class WorkflowRunStore:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store
        self._ensure_schema()

    def _conn(self):
        return self.store._connect()

    def _ensure_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS workflow_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    workflow_version INTEGER NOT NULL,
                    draft_id INTEGER,
                    topic TEXT NOT NULL,
                    ok INTEGER NOT NULL,
                    steps_json TEXT NOT NULL,
                    mutation_notes_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL
                );
                """
            )

    def record(self, run: WorkflowRun) -> int:
        now = _utc_now()
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO workflow_runs
                (workflow_id, workflow_version, draft_id, topic, ok, steps_json, mutation_notes_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.workflow_id,
                    run.workflow_version,
                    run.draft_id,
                    run.topic[:200],
                    1 if run.ok else 0,
                    json.dumps([s.to_dict() for s in run.step_results]),
                    json.dumps(run.mutation_notes),
                    now,
                ),
            )
            return int(cur.lastrowid)

    def recent(self, *, workflow_id: str = "daily_invideo", limit: int = 20) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT id, workflow_id, workflow_version, draft_id, topic, ok,
                       steps_json, mutation_notes_json, created_at
                FROM workflow_runs
                WHERE workflow_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (workflow_id, limit),
            ).fetchall()
        out: list[dict] = []
        for row in rows:
            out.append(
                {
                    "id": row[0],
                    "workflow_id": row[1],
                    "workflow_version": row[2],
                    "draft_id": row[3],
                    "topic": row[4],
                    "ok": bool(row[5]),
                    "steps": json.loads(row[6] or "[]"),
                    "mutation_notes": json.loads(row[7] or "[]"),
                    "created_at": row[8],
                }
            )
        return out

    def step_failure_streak(self, step_id: str, *, workflow_id: str = "daily_invideo", limit: int = 5) -> int:
        """How many recent runs failed at this step (consecutive from newest)."""
        streak = 0
        for row in self.recent(workflow_id=workflow_id, limit=limit):
            steps = {s["step_id"]: s for s in row.get("steps") or []}
            hit = steps.get(step_id)
            if hit and not hit.get("ok"):
                streak += 1
            else:
                break
        return streak
