from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Draft:
    id: int
    topic: str
    script: str
    hook: str
    help_angle: str
    status: str
    quality_notes: str
    created_at: str
    reviewed_at: str | None
    review_note: str | None


class MemoryStore:
    """SQLite-backed memory for drafts, approvals, and learned feedback."""

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
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS drafts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    script TEXT NOT NULL,
                    hook TEXT NOT NULL,
                    help_angle TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    quality_notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    reviewed_at TEXT,
                    review_note TEXT
                );

                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    draft_id INTEGER NOT NULL,
                    decision TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (draft_id) REFERENCES drafts(id)
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS channel_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )

    def set_channel_state(self, key: str, value: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO channel_state (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                (key, value, _utc_now()),
            )

    def get_channel_state(self, key: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute("SELECT value FROM channel_state WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def channel_summary(self) -> dict[str, str | None]:
        return {
            "ready": self.get_channel_state("ready"),
            "channel_name": self.get_channel_state("channel_name"),
            "note": self.get_channel_state("note"),
            "updated_at": self.get_channel_state("updated_at"),
        }

    def mark_channel_ready(self, channel_name: str | None = None, note: str = "") -> None:
        now = _utc_now()
        self.set_channel_state("ready", "true")
        self.set_channel_state("updated_at", now)
        if channel_name:
            self.set_channel_state("channel_name", channel_name)
        if note:
            self.set_channel_state("note", note)

    def save_draft(
        self,
        topic: str,
        script: str,
        hook: str,
        help_angle: str,
        quality_notes: str = "",
    ) -> Draft:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO drafts (topic, script, hook, help_angle, quality_notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (topic, script, hook, help_angle, quality_notes, _utc_now()),
            )
            draft_id = int(cur.lastrowid)
        return self.get_draft(draft_id)

    def get_draft(self, draft_id: int) -> Draft:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
        if row is None:
            raise KeyError(f"Draft {draft_id} not found")
        return self._row_to_draft(row)

    def update_draft_content(
        self,
        draft_id: int,
        *,
        script: str | None = None,
        hook: str | None = None,
        help_angle: str | None = None,
        quality_notes: str | None = None,
    ) -> Draft:
        draft = self.get_draft(draft_id)
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE drafts
                SET script = ?, hook = ?, help_angle = ?, quality_notes = ?
                WHERE id = ?
                """,
                (
                    script if script is not None else draft.script,
                    hook if hook is not None else draft.hook,
                    help_angle if help_angle is not None else draft.help_angle,
                    quality_notes if quality_notes is not None else draft.quality_notes,
                    draft_id,
                ),
            )
        return self.get_draft(draft_id)

    def list_drafts(self, status: str | None = None, limit: int = 20) -> list[Draft]:
        query = "SELECT * FROM drafts"
        params: list[Any] = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_draft(row) for row in rows]

    def review_draft(self, draft_id: int, decision: str, reason: str) -> Draft:
        if decision not in {"approved", "rejected"}:
            raise ValueError("decision must be approved or rejected")
        draft = self.get_draft(draft_id)
        reviewed_at = _utc_now()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE drafts
                SET status = ?, reviewed_at = ?, review_note = ?
                WHERE id = ?
                """,
                (decision, reviewed_at, reason, draft_id),
            )
            conn.execute(
                """
                INSERT INTO feedback (draft_id, decision, reason, topic, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (draft_id, decision, reason, draft.topic, reviewed_at),
            )
        return self.get_draft(draft_id)

    def learned_patterns(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT decision, reason, topic, created_at
                FROM feedback
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def rejection_summary(self) -> list[str]:
        patterns = self.learned_patterns(limit=50)
        return [
            f"[{p['decision']}] {p['topic']}: {p['reason']}"
            for p in patterns
            if p["decision"] == "rejected"
        ]

    def approval_summary(self) -> list[str]:
        patterns = self.learned_patterns(limit=50)
        return [
            f"[{p['decision']}] {p['topic']}: {p['reason']}"
            for p in patterns
            if p["decision"] == "approved"
        ]

    def save_chat(self, role: str, content: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO chat_messages (role, content, created_at) VALUES (?, ?, ?)",
                (role, content, _utc_now()),
            )

    def recent_chat(self, limit: int = 20) -> list[dict[str, str]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content FROM chat_messages
                ORDER BY id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

    @staticmethod
    def _row_to_draft(row: sqlite3.Row) -> Draft:
        return Draft(
            id=row["id"],
            topic=row["topic"],
            script=row["script"],
            hook=row["hook"],
            help_angle=row["help_angle"],
            status=row["status"],
            quality_notes=row["quality_notes"],
            created_at=row["created_at"],
            reviewed_at=row["reviewed_at"],
            review_note=row["review_note"],
        )

    def stats(self) -> dict[str, int]:
        with self._connect() as conn:
            pending = conn.execute(
                "SELECT COUNT(*) FROM drafts WHERE status = 'pending'"
            ).fetchone()[0]
            approved = conn.execute(
                "SELECT COUNT(*) FROM drafts WHERE status = 'approved'"
            ).fetchone()[0]
            rejected = conn.execute(
                "SELECT COUNT(*) FROM drafts WHERE status = 'rejected'"
            ).fetchone()[0]
        return {"pending": pending, "approved": approved, "rejected": rejected}
