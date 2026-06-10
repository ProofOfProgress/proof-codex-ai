"""Persistent agent memory — operating rules, preferences, facts (ChatGPT-style)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore, _utc_now

CATEGORIES = ("operating_rule", "preference", "fact", "context", "decision")


@dataclass
class AgentMemory:
    id: int
    category: str
    title: str
    content: str
    source: str
    pinned: bool
    created_at: str
    updated_at: str


def _default_seed_path() -> Path:
    return Path("data/operating_rules_seed.md")


class AgentMemoryStore:
    """SQLite-backed long-term memory + MEMORY.md export."""

    def __init__(self, store: MemoryStore) -> None:
        self.store = store
        self._init_table()
        self._seed_if_empty()

    def _conn(self):
        return self.store._connect()

    def _init_table(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL DEFAULT 'fact',
                    title TEXT NOT NULL DEFAULT '',
                    content TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'user',
                    pinned INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def _seed_if_empty(self) -> None:
        if self.list_memories(limit=1):
            return
        seed = _default_seed_path()
        if seed.exists():
            self.import_markdown(seed, source="seed", category="operating_rule")
        else:
            self._seed_builtin()

    def _seed_builtin(self) -> None:
        defaults = [
            (
                "operating_rule",
                "Niche v2",
                "Channel niche is The Minute Before — one specific high-stakes moment, one concrete fix. "
                "Not generic sleep/anxiety lists.",
            ),
            (
                "operating_rule",
                "Pipeline",
                "Paid stack: Gemini → Resemble voice → TurboScribe (or script timing) → AI images → "
                "ffmpeg ASS captions → YouTube API upload. API first; use Playwright browser "
                "for vidIQ, Trends, logins, and pages that block HTTP.",
            ),
            (
                "operating_rule",
                "Captions",
                "CAPTION_MODE=ffmpeg — Jenny 05 safe zone (~320px above bottom). Subject in upper 60% of frame.",
            ),
            (
                "operating_rule",
                "Accounts",
                "Google/YouTube/Gemini: paypalacc4progress@gmail.com. Channel: Soft Continuity.",
            ),
            (
                "operating_rule",
                "Strategist behavior",
                "Do not ask clarifying questions unless impossible to proceed. Infer intent and act.",
            ),
            (
                "preference",
                "Discord control",
                "User controls pipeline via Discord: daily, research, apply brand, finish video.",
            ),
            (
                "operating_rule",
                "Deep research",
                "Deep research = web browse + Google Trends + YouTube competitors + vidIQ keywords + "
                "Jenny course synthesis. Not local files only. Include recommended_path for fastest pipeline run.",
            ),
        ]
        for cat, title, content in defaults:
            self.add_memory(category=cat, title=title, content=content, source="seed", pinned=True)

    def add_memory(
        self,
        *,
        content: str,
        category: str = "fact",
        title: str = "",
        source: str = "user",
        pinned: bool = False,
    ) -> AgentMemory:
        content = content.strip()
        if not content:
            raise ValueError("Memory content cannot be empty.")
        cat = category if category in CATEGORIES else "fact"
        title = (title or content[:60]).strip()
        now = _utc_now()
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO agent_memories (category, title, content, source, pinned, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (cat, title, content, source, 1 if pinned else 0, now, now),
            )
            mid = int(cur.lastrowid)
        self.export_markdown()
        return self.get_memory(mid)

    def get_memory(self, memory_id: int) -> AgentMemory:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM agent_memories WHERE id = ?", (memory_id,)).fetchone()
        if row is None:
            raise KeyError(memory_id)
        return self._row(row)

    def list_memories(
        self,
        *,
        category: str | None = None,
        limit: int = 50,
    ) -> list[AgentMemory]:
        q = "SELECT * FROM agent_memories"
        params: list[object] = []
        if category:
            q += " WHERE category = ?"
            params.append(category)
        q += " ORDER BY pinned DESC, updated_at DESC LIMIT ?"
        params.append(limit)
        with self._conn() as conn:
            rows = conn.execute(q, params).fetchall()
        return [self._row(r) for r in rows]

    def delete_memory(self, memory_id: int) -> bool:
        with self._conn() as conn:
            cur = conn.execute("DELETE FROM agent_memories WHERE id = ?", (memory_id,))
        if cur.rowcount:
            self.export_markdown()
            return True
        return False

    def update_memory(self, memory_id: int, *, content: str | None = None, title: str | None = None) -> AgentMemory:
        mem = self.get_memory(memory_id)
        new_content = content.strip() if content else mem.content
        new_title = title.strip() if title else mem.title
        with self._conn() as conn:
            conn.execute(
                "UPDATE agent_memories SET content = ?, title = ?, updated_at = ? WHERE id = ?",
                (new_content, new_title, _utc_now(), memory_id),
            )
        self.export_markdown()
        return self.get_memory(memory_id)

    def context_block(self, *, max_chars: int = 4000) -> str:
        """Inject into system prompts — pinned + operating rules first."""
        mems = self.list_memories(limit=40)
        if not mems:
            return ""
        lines = ["LONG-TERM MEMORY (follow unless user overrides):"]
        used = 0
        for m in mems:
            line = f"- [{m.category}] {m.title}: {m.content}"
            if used + len(line) > max_chars:
                break
            lines.append(line)
            used += len(line)
        return "\n".join(lines)

    def format_list(self, *, limit: int = 20) -> str:
        mems = self.list_memories(limit=limit)
        if not mems:
            return "No memories saved yet. Say: `remember <fact>` or `!remember <text>`"
        lines = ["**Agent memory**"]
        for m in mems:
            pin = "📌 " if m.pinned else ""
            lines.append(f"{pin}#{m.id} [{m.category}] **{m.title}** — {m.content[:120]}")
        lines.append("\nForget: `forget <id>` · Add: `remember <text>`")
        return "\n".join(lines)

    def export_markdown(self, path: Path | None = None) -> Path:
        out = path or settings.memory_markdown_path
        out.parent.mkdir(parents=True, exist_ok=True)
        mems = self.list_memories(limit=100)
        lines = [
            "# Agent memory — Soft Continuity",
            "",
            f"_Updated {datetime.now(timezone.utc).isoformat()}_",
            "",
            "Pinned operating rules and facts the bot remembers across sessions.",
            "",
        ]
        by_cat: dict[str, list[AgentMemory]] = {}
        for m in mems:
            by_cat.setdefault(m.category, []).append(m)
        for cat in CATEGORIES:
            if cat not in by_cat:
                continue
            lines.append(f"## {cat.replace('_', ' ').title()}")
            lines.append("")
            for m in by_cat[cat]:
                pin = " (pinned)" if m.pinned else ""
                lines.append(f"### #{m.id} {m.title}{pin}")
                lines.append("")
                lines.append(m.content)
                lines.append("")
        out.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        return out

    def import_markdown(self, path: Path, *, source: str = "import", category: str = "operating_rule") -> int:
        text = path.read_text(encoding="utf-8")
        count = 0
        for block in re.split(r"\n##+ ", text):
            block = block.strip()
            if not block or block.startswith("# Agent memory"):
                continue
            lines = block.splitlines()
            heading = lines[0].strip()
            body = "\n".join(lines[1:]).strip()
            if not body or len(body) < 10:
                continue
            title = heading.lstrip("#").strip()[:80]
            self.add_memory(category=category, title=title, content=body, source=source, pinned=True)
            count += 1
        return count

    @staticmethod
    def _row(row) -> AgentMemory:
        return AgentMemory(
            id=row["id"],
            category=row["category"],
            title=row["title"],
            content=row["content"],
            source=row["source"],
            pinned=bool(row["pinned"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


_REMEMBER_PATTERNS = (
    re.compile(r"^remember(?:\s+that)?:\s*(.+)$", re.I),
    re.compile(r"^remember\s+(.+)$", re.I),
    re.compile(r"^operating rule:\s*(.+)$", re.I),
    re.compile(r"^save (?:to )?memory:\s*(.+)$", re.I),
    re.compile(r"^don'?t forget:\s*(.+)$", re.I),
    re.compile(r"^always remember:\s*(.+)$", re.I),
)

_FORGET_PATTERN = re.compile(r"^forget(?:\s+memory)?\s+#?(\d+)\s*$", re.I)
_MEMORY_LIST = frozenset({"memory", "memories", "my memory", "what do you remember", "operating rules", "rules"})


def parse_remember_request(message: str) -> tuple[str, str] | None:
    """Return (category, content) if message is a remember command."""
    text = message.strip()
    for pat in _REMEMBER_PATTERNS:
        m = pat.match(text)
        if m:
            body = m.group(1).strip()
            if not body:
                return None
            cat = "operating_rule" if "operating rule" in text.lower() else "fact"
            if body.lower().startswith("preference ") or "prefer " in body.lower()[:20]:
                cat = "preference"
            return cat, body
    return None


def parse_forget_request(message: str) -> int | None:
    m = _FORGET_PATTERN.match(message.strip())
    return int(m.group(1)) if m else None


def is_memory_list_request(message: str) -> bool:
    return message.strip().lower() in _MEMORY_LIST


def get_agent_memory_store(store: MemoryStore | None = None) -> AgentMemoryStore:
    s = store or MemoryStore(settings.database_path)
    return AgentMemoryStore(s)
