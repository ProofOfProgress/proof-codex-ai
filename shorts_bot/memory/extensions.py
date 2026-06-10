from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
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

                CREATE TABLE IF NOT EXISTS scheduled_publishes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    draft_id INTEGER,
                    video_id TEXT NOT NULL UNIQUE,
                    visibility TEXT NOT NULL DEFAULT 'unlisted',
                    uploaded_at TEXT NOT NULL,
                    publish_at TEXT NOT NULL,
                    published_at TEXT
                );

                CREATE TABLE IF NOT EXISTS comment_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    youtube_comment_id TEXT NOT NULL UNIQUE,
                    video_id TEXT NOT NULL,
                    author TEXT NOT NULL DEFAULT '',
                    original_text TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    reason TEXT NOT NULL DEFAULT '',
                    reply_text TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS upload_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    draft_id INTEGER,
                    topic TEXT NOT NULL,
                    hook TEXT NOT NULL DEFAULT '',
                    script TEXT NOT NULL DEFAULT '',
                    title TEXT NOT NULL DEFAULT '',
                    video_id TEXT NOT NULL DEFAULT '',
                    uploaded_at TEXT NOT NULL
                );
                """
            )
            try:
                conn.execute("ALTER TABLE reward_events ADD COLUMN breakdown_json TEXT")
            except Exception:
                pass

    def save_analytics(self, video_label: str, metrics: dict[str, Any]) -> None:
        """Upsert — latest metrics per video replace older rows."""
        now = _utc_now()
        with self._conn() as conn:
            conn.execute("DELETE FROM analytics_records WHERE video_label = ?", (video_label,))
            conn.execute(
                "INSERT INTO analytics_records (video_label, metrics_json, recorded_at) VALUES (?, ?, ?)",
                (video_label, json.dumps(metrics), now),
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
        else:
            hint = f"{imp.title}: {note or imp.description}"[:500]
            self.set_training_config(f"rejected:{improvement_id}", hint)
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

    def _config_values(self, prefix: str, *, limit: int = 10) -> list[str]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT value FROM training_config WHERE key LIKE ? ORDER BY updated_at DESC LIMIT ?",
                (f"{prefix}%", limit),
            ).fetchall()
        return [r["value"] for r in rows]

    def avoid_patterns(self) -> list[str]:
        return self._config_values("avoid:", limit=8)

    def repeat_patterns(self) -> list[str]:
        return self._config_values("repeat:", limit=6)

    def rejected_training_hints(self) -> list[str]:
        return self._config_values("rejected:", limit=6)

    def recent_performance_context(self, *, limit: int = 3) -> str:
        rewards = self.recent_rewards(limit=limit)
        if not rewards:
            return ""
        lines = ["RECENT VIDEO PERFORMANCE (learn from these):"]
        for r in rewards:
            lines.append(
                f"- {r['video_label']}: {r['verdict']} ({r['score']:+.2f}) — {r['reason'][:120]}"
            )
        return "\n".join(lines)

    def applied_training_context(self) -> str:
        """Unified self-learning block for drafts + strategist."""
        parts: list[str] = []
        rules = self.applied_improvements()
        if rules:
            parts.append("APPROVED TRAINING RULES:\n" + "\n".join(f"- {r}" for r in rules[:10]))
        avoid = self.avoid_patterns()
        rejected = self.rejected_training_hints()
        if avoid or rejected:
            lines = avoid + [f"(rejected proposal) {h}" for h in rejected]
            parts.append("AVOID / DO NOT REPEAT:\n" + "\n".join(f"- {x}" for x in lines[:10]))
        repeat = self.repeat_patterns()
        if repeat:
            parts.append("REPEAT WHEN RELEVANT:\n" + "\n".join(f"- {r}" for r in repeat[:6]))
        perf = self.recent_performance_context()
        if perf:
            parts.append(perf)
        return "\n\n".join(parts)

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
            from shorts_bot.automation.dev_queue import export_dev_queue

            export_dev_queue(self)
        return task

    def schedule_publish(
        self,
        *,
        video_id: str,
        draft_id: int | None = None,
        visibility: str = "unlisted",
        publish_after_hours: int,
    ) -> None:
        if publish_after_hours <= 0:
            return
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        publish_at = now + timedelta(hours=publish_after_hours)
        uploaded_at = _utc_now()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO scheduled_publishes
                    (draft_id, video_id, visibility, uploaded_at, publish_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(video_id) DO UPDATE SET
                    draft_id = excluded.draft_id,
                    visibility = excluded.visibility,
                    uploaded_at = excluded.uploaded_at,
                    publish_at = excluded.publish_at,
                    published_at = NULL
                """,
                (
                    draft_id,
                    video_id,
                    visibility,
                    uploaded_at,
                    publish_at.isoformat(),
                ),
            )

    def list_due_scheduled_publishes(self, *, limit: int = 10) -> list[dict[str, Any]]:
        now = _utc_now()
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT video_id, draft_id, visibility, publish_at
                FROM scheduled_publishes
                WHERE published_at IS NULL AND publish_at <= ?
                ORDER BY publish_at ASC
                LIMIT ?
                """,
                (now, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def mark_scheduled_published(self, video_id: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE scheduled_publishes SET published_at = ? WHERE video_id = ?",
                (_utc_now(), video_id),
            )

    def comment_already_handled(self, youtube_comment_id: str) -> bool:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT 1 FROM comment_actions WHERE youtube_comment_id = ? LIMIT 1",
                (youtube_comment_id,),
            ).fetchone()
        return row is not None

    def record_comment_action(
        self,
        *,
        comment_id: str,
        video_id: str,
        author: str,
        original_text: str,
        decision: str,
        reason: str = "",
        reply_text: str | None = None,
    ) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO comment_actions
                    (youtube_comment_id, video_id, author, original_text, decision, reason, reply_text, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(youtube_comment_id) DO UPDATE SET
                    decision = excluded.decision,
                    reason = excluded.reason,
                    reply_text = excluded.reply_text,
                    created_at = excluded.created_at
                """,
                (
                    comment_id,
                    video_id,
                    author[:120],
                    original_text[:2000],
                    decision,
                    reason[:500],
                    reply_text[:2000] if reply_text else None,
                    _utc_now(),
                ),
            )

    def list_comments_needing_human(self, *, limit: int = 20) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT youtube_comment_id, video_id, author, original_text, reason, created_at
                FROM comment_actions
                WHERE decision = 'needs_human'
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def count_comments_needing_human(self) -> int:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS n FROM comment_actions WHERE decision = 'needs_human'"
            ).fetchone()
        return int(row["n"]) if row else 0

    def record_upload_event(
        self,
        *,
        draft_id: int,
        topic: str,
        hook: str,
        script: str,
        title: str,
        video_id: str,
    ) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO upload_events
                    (draft_id, topic, hook, script, title, video_id, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    draft_id,
                    topic[:200],
                    hook[:300],
                    script[:4000],
                    title[:200],
                    video_id,
                    _utc_now(),
                ),
            )

    def recent_uploads(self, *, hours: int = 24) -> list[dict[str, Any]]:
        cutoff = (
            datetime.now(timezone.utc) - timedelta(hours=hours)
        ).isoformat()
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT draft_id, topic, hook, title, video_id, uploaded_at
                FROM upload_events
                WHERE uploaded_at >= ?
                ORDER BY id DESC
                """,
                (cutoff,),
            ).fetchall()
        return [dict(r) for r in rows]

    def recent_upload_scripts(self, *, limit: int = 5) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT draft_id, topic, hook, script, title, uploaded_at
                FROM upload_events
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def topic_uploaded_within_days(self, topic: str, *, days: int) -> bool:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT 1 FROM upload_events
                WHERE lower(topic) = lower(?) AND uploaded_at >= ?
                LIMIT 1
                """,
                (topic.strip(), cutoff),
            ).fetchone()
        return row is not None

    def hook_uploaded_within_days(self, hook: str, *, days: int) -> bool:
        if not hook.strip():
            return False
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT 1 FROM upload_events
                WHERE lower(hook) = lower(?) AND uploaded_at >= ?
                LIMIT 1
                """,
                (hook.strip()[:120], cutoff),
            ).fetchone()
        return row is not None

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
