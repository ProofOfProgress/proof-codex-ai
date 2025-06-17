from dataclasses import dataclass
from pathlib import Path
import json
import re
from typing import List, Iterable


@dataclass
class CodexEntry:
    """Represents an entry extracted from a task log."""
    tag: str
    content: str


class CodexTaskParser:
    """Parses new task logs and converts them into codex entries."""

    LOG_PATTERN = re.compile(r"\[(?P<tag>[A-Z]+):\]\s*(?P<content>.*)")

    def __init__(self, log_dir: Path):
        self.log_dir = Path(log_dir)
        self.state_file = self.log_dir / "processed_logs.json"
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True)
        self.processed_files = set()
        if self.state_file.exists():
            try:
                self.processed_files = set(json.loads(self.state_file.read_text()))
            except Exception:
                self.processed_files = set()

    def _save_state(self) -> None:
        self.state_file.write_text(json.dumps(list(self.processed_files)))

    def parse_logs(self) -> List[CodexEntry]:
        """Parse new logs in the directory and return codex entries."""
        entries: List[CodexEntry] = []
        for log_file in sorted(self.log_dir.glob("*.log")):
            if log_file.name in self.processed_files:
                continue
            for line in log_file.read_text().splitlines():
                match = self.LOG_PATTERN.match(line.strip())
                if match:
                    entries.append(
                        CodexEntry(tag=match.group("tag"), content=match.group("content"))
                    )
            self.processed_files.add(log_file.name)
        if entries:
            self._save_state()
        return entries
