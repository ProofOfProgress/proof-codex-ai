"""Persist manager work jobs for async polling (web UI)."""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ManagerJob:
    id: str
    message: str
    work_seconds: int
    status: str  # queued | running | done | error
    reply: str | None
    work_log: list[dict[str, Any]]
    created_at: str
    started_at: str | None
    finished_at: str | None
    error: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "message": self.message,
            "work_seconds": self.work_seconds,
            "status": self.status,
            "reply": self.reply,
            "work_log": self.work_log,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
        }


class ManagerJobStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS manager_jobs (
                    id TEXT PRIMARY KEY,
                    message TEXT NOT NULL,
                    work_seconds INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'queued',
                    reply TEXT,
                    work_log TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT,
                    error TEXT
                )
                """
            )

    def create(self, message: str, work_seconds: int = 0) -> ManagerJob:
        job_id = uuid.uuid4().hex[:12]
        now = _utc_now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO manager_jobs
                (id, message, work_seconds, status, work_log, created_at)
                VALUES (?, ?, ?, 'queued', '[]', ?)
                """,
                (job_id, message, work_seconds, now),
            )
        return self.get(job_id)

    def get(self, job_id: str) -> ManagerJob:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM manager_jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(f"Manager job {job_id} not found")
        return self._row_to_job(row)

    def update(
        self,
        job_id: str,
        *,
        status: str | None = None,
        reply: str | None = None,
        work_log: list[dict[str, Any]] | None = None,
        started_at: str | None = None,
        finished_at: str | None = None,
        error: str | None = None,
    ) -> ManagerJob:
        job = self.get(job_id)
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE manager_jobs
                SET status = ?, reply = ?, work_log = ?,
                    started_at = ?, finished_at = ?, error = ?
                WHERE id = ?
                """,
                (
                    status or job.status,
                    reply if reply is not None else job.reply,
                    json.dumps(work_log if work_log is not None else job.work_log),
                    started_at if started_at is not None else job.started_at,
                    finished_at if finished_at is not None else job.finished_at,
                    error if error is not None else job.error,
                    job_id,
                ),
            )
        return self.get(job_id)

    def list_recent(self, limit: int = 20) -> list[ManagerJob]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM manager_jobs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_job(r) for r in rows]

    @staticmethod
    def _row_to_job(row: sqlite3.Row) -> ManagerJob:
        log_raw = row["work_log"] or "[]"
        try:
            work_log = json.loads(log_raw)
        except json.JSONDecodeError:
            work_log = []
        return ManagerJob(
            id=row["id"],
            message=row["message"],
            work_seconds=int(row["work_seconds"]),
            status=row["status"],
            reply=row["reply"],
            work_log=work_log,
            created_at=row["created_at"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            error=row["error"],
        )
