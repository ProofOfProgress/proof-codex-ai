from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.memory.extensions import DevTask, Improvement


class LearnedFile:
    """Human-readable journal of approved training rules."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def _stamp(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    def _append(self, block: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        header = ""
        if not self.path.exists():
            header = "# Shorts Bot — learned rules\n\nApproved improvements and dev tasks appear here.\n\n"
        with self.path.open("a", encoding="utf-8") as f:
            if header:
                f.write(header)
            f.write(block)
            if not block.endswith("\n"):
                f.write("\n")

    def record_improvement(self, imp: Improvement, *, approved: bool) -> None:
        if not approved:
            return
        self._append(
            f"## [{self._stamp()}] Improvement: {imp.title}\n"
            f"- Category: {imp.category}\n"
            f"- Rule: {imp.description}\n"
        )

    def record_dev_task(self, task: DevTask, *, approved: bool) -> None:
        if not approved:
            return
        self._append(
            f"## [{self._stamp()}] Dev: {task.title}\n"
            f"- Request: {task.description}\n"
        )

    def read_tail(self, max_chars: int = 4000) -> str:
        if not self.path.exists():
            return "No learned rules yet — approve improvements to build this file."
        text = self.path.read_text(encoding="utf-8")
        if len(text) <= max_chars:
            return text
        return "…\n" + text[-max_chars:]
