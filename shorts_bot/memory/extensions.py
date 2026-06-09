from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from shorts_bot.memory.store import MemoryStore, _utc_now


@dataclass
class Improvement:
    id: int
    title: str
    category: str
    description: str
    pros: list[str]
    cons: list[str]
    status: str
    source: str
    created_at: str
    reviewed_at: str | None
    review_note: str | None


@dataclass
class RewardEvent:
    id: int
    video_label: str
    score: float
    verdict: str
    reason: str
    metrics: dict[str, Any]
    created_at: str
    breakdown: list[dict[str, Any]] | None = None


@dataclass
class DevTask:
    id: int
    title: str
    description: str
    pros: list[str]
    cons: list[str]
    status: str
    source: str
    created_at: str
    reviewed_at: str | None
    review_note: str | None


class MemoryExtensions:
    """Analytics, rewards, and improvement proposals on top of MemoryStore."""

    def __init__(self, store: MemoryStore) -> None:
        self.store = store
        self._init_tables()

    def _conn(self):
        return self.store._connect()

    def _init_tables(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS analytics_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_label TEXT NOT NULL,
                    metrics_json TEXT NOT NULL,
                    recorded_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS reward_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_label TEXT NOT NULL,
                    score REAL NOT NULL,
                    verdict TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    metrics_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS improvements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    pros_json TEXT NOT NULL,
                    cons_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    source TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    reviewed_at TEXT,
                    review_note TEXT
                );

                CREATE TABLE IF NOT EXISTS training_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS dev_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    pros_json TEXT NOT NULL,
                    cons_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    source TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    reviewed_at TEXT,
                    review_note TEXT
                );
                """
            )
            try:
                conn.execute("ALTER TABLE reward_events ADD COLUMN breakdown_json TEXT")
            except Exception:
                pass

    def save_analytics(self, video_label: str, metrics: dict[str, Any]) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO analytics_records (video_label, metrics_json, recorded_at) VALUES (?, ?, ?)",
                (video_label, json.dumps(metrics), _utc_now()),
            )

    def list_analytics(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT video_label, metrics_json, recorded_at FROM analytics_records ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {"video_label": r["video_label"], "metrics": json.loads(r["metrics_json"]), "recorded_at": r["recorded_at"]}
            for r in rows
        ]

    def save_reward(self, event: RewardEvent) -> None:
        breakdown = json.dumps(event.breakdown or [])
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO reward_events (video_label, score, verdict, reason, metrics_json, created_at, breakdown_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.video_label,
                    event.score,
                    event.verdict,
                    event.reason,
                    json.dumps(event.metrics),
                    event.created_at,
                    breakdown,
                ),
            )

    def recent_rewards(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM reward_events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        out = []
        for r in rows:
            raw_bd = r["breakdown_json"] if "breakdown_json" in r.keys() else None
            out.append(
                {
                    "id": r["id"],
                    "video_label": r["video_label"],
                    "score": r["score"],
                    "verdict": r["verdict"],
                    "reason": r["reason"],
                    "metrics": json.loads(r["metrics_json"]),
                    "breakdown": json.loads(raw_bd) if raw_bd else [],
                    "created_at": r["created_at"],
                }
            )
        return out

    def find_pending_by_title(self, title: str) -> Improvement | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM improvements WHERE status = 'pending' AND lower(title) = lower(?) LIMIT 1",
                (title.strip(),),
            ).fetchone()
        return self._row_improvement(row) if row else None

    def create_improvement(
        self,
        *,
        title: str,
        category: str,
        description: str,
        pros: list[str],
        cons: list[str],
        source: str = "",
    ) -> Improvement:
        existing = self.find_pending_by_title(title)
        if existing:
            return existing
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO improvements (title, category, description, pros_json, cons_json, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (title, category, description, json.dumps(pros), json.dumps(cons), source, _utc_now()),
            )
            iid = int(cur.lastrowid)
        return self.get_improvement(iid)

    def get_improvement(self, improvement_id: int) -> Improvement:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM improvements WHERE id = ?", (improvement_id,)).fetchone()
        if row is None:
            raise KeyError(improvement_id)
        return self._row_improvement(row)

    def list_improvements(self, status: str | None = "pending", limit: int = 20) -> list[Improvement]:
        q = "SELECT * FROM improvements"
        params: list[Any] = []
        if status:
            q += " WHERE status = ?"
            params.append(status)
        q += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with self._conn() as conn:
            rows = conn.execute(q, params).fetchall()
        return [self._row_improvement(r) for r in rows]

    def review_improvement(self, improvement_id: int, approved: bool, note: str = "") -> Improvement:
        decision = "approved" if approved else "rejected"
        with self._conn() as conn:
            conn.execute(
                "UPDATE improvements SET status = ?, reviewed_at = ?, review_note = ? WHERE id = ?",
                (decision, _utc_now(), note, improvement_id),
            )
        imp = self.get_improvement(improvement_id)
        if approved:
            self.set_training_config(f"applied:{improvement_id}", imp.description)
        return imp

    def set_training_config(self, key: str, value: str) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO training_config (key, value, updated_at) VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                (key, value, _utc_now()),
            )

    def get_training_config(self, key: str) -> str | None:
        with self._conn() as conn:
            row = conn.execute("SELECT value FROM training_config WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def applied_improvements(self) -> list[str]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT value FROM training_config WHERE key LIKE 'applied:%' ORDER BY updated_at DESC"
            ).fetchall()
        return [r["value"] for r in rows]

    def applied_training_context(self) -> str:
        rules = self.applied_improvements()
        if not rules:
            return ""
        return "Approved training rules (follow these):\n" + "\n".join(f"- {r}" for r in rules[:12])

    def find_pending_dev_by_title(self, title: str) -> DevTask | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM dev_tasks WHERE status = 'pending' AND lower(title) = lower(?) LIMIT 1",
                (title.strip(),),
            ).fetchone()
        return self._row_dev_task(row) if row else None

    def create_dev_task(
        self,
        *,
        title: str,
        description: str,
        pros: list[str] | None = None,
        cons: list[str] | None = None,
        source: str = "user",
    ) -> DevTask:
        existing = self.find_pending_dev_by_title(title)
        if existing:
            return existing
        pros = pros or ["Ships capability you asked for", "Queued for approval before any auto-work"]
        cons = cons or ["May need your login later for external services", "Complex tasks split into smaller steps"]
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO dev_tasks (title, description, pros_json, cons_json, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (title, description, json.dumps(pros), json.dumps(cons), source, _utc_now()),
            )
            tid = int(cur.lastrowid)
        return self.get_dev_task(tid)

    def get_dev_task(self, task_id: int) -> DevTask:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM dev_tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise KeyError(task_id)
        return self._row_dev_task(row)

    def list_dev_tasks(self, status: str | None = "pending", limit: int = 20) -> list[DevTask]:
        q = "SELECT * FROM dev_tasks"
        params: list[Any] = []
        if status:
            q += " WHERE status = ?"
            params.append(status)
        q += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with self._conn() as conn:
            rows = conn.execute(q, params).fetchall()
        return [self._row_dev_task(r) for r in rows]

    def review_dev_task(self, task_id: int, approved: bool, note: str = "") -> DevTask:
        decision = "approved" if approved else "rejected"
        with self._conn() as conn:
            conn.execute(
                "UPDATE dev_tasks SET status = ?, reviewed_at = ?, review_note = ? WHERE id = ?",
                (decision, _utc_now(), note, task_id),
            )
        task = self.get_dev_task(task_id)
        if approved:
            self.set_training_config(f"dev:{task_id}", task.description)
        return task

    def learning_journal(self, limit: int = 15) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        with self._conn() as conn:
            imp_rows = conn.execute(
                """
                SELECT 'improvement' AS kind, id, title, status, review_note, reviewed_at
                FROM improvements WHERE status != 'pending' ORDER BY reviewed_at DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
            dev_rows = conn.execute(
                """
                SELECT 'dev' AS kind, id, title, status, review_note, reviewed_at
                FROM dev_tasks WHERE status != 'pending' ORDER BY reviewed_at DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        for r in imp_rows:
            entries.append(dict(r))
        for r in dev_rows:
            entries.append(dict(r))
        entries.sort(key=lambda e: e.get("reviewed_at") or "", reverse=True)
        return entries[:limit]

    @staticmethod
    def _row_improvement(row) -> Improvement:
        return Improvement(
            id=row["id"],
            title=row["title"],
            category=row["category"],
            description=row["description"],
            pros=json.loads(row["pros_json"]),
            cons=json.loads(row["cons_json"]),
            status=row["status"],
            source=row["source"],
            created_at=row["created_at"],
            reviewed_at=row["reviewed_at"],
            review_note=row["review_note"],
        )

    @staticmethod
    def _row_dev_task(row) -> DevTask:
        return DevTask(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            pros=json.loads(row["pros_json"]),
            cons=json.loads(row["cons_json"]),
            status=row["status"],
            source=row["source"],
            created_at=row["created_at"],
            reviewed_at=row["reviewed_at"],
            review_note=row["review_note"],
        )
