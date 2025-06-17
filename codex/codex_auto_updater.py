from datetime import datetime
from pathlib import Path
from typing import Iterable

from .codex_task_parser import CodexTaskParser, CodexEntry


def update_master_codex(master_codex_path: Path, log_dir: Path) -> None:
    """Append new codex entries from task logs to the master codex file."""
    parser = CodexTaskParser(log_dir)
    entries = parser.parse_logs()
    if not entries:
        return

    master_codex_path = Path(master_codex_path)
    if not master_codex_path.exists():
        master_codex_path.touch()

    with master_codex_path.open("a") as f:
        f.write(f"\n# Updated on {datetime.utcnow().isoformat()}\n")
        for entry in entries:
            f.write(f"[{entry.tag}:] {entry.content}\n")
