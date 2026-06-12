"""Export approved dev tasks for cloud agents."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.memory.extensions import MemoryExtensions


def export_dev_queue(memory: MemoryExtensions) -> Path:
    """Rewrite data/DEV_QUEUE.md from approved dev:* training_config + dev_tasks table."""
    path = settings.data_dir / "DEV_QUEUE.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    approved = memory.list_dev_tasks(status="approved", limit=50)
    lines = [
        "# Dev queue (approved — cloud agent picks up)",
        "",
        "_Auto-exported. Login/payment tasks still need you._",
        "",
    ]
    if not approved:
        lines.append("_No approved dev tasks yet._")
    else:
        for task in approved:
            lines.extend(
                [
                    f"## #{task.id} {task.title}",
                    "",
                    task.description.strip(),
                    "",
                    f"_Approved {task.reviewed_at or task.created_at}_",
                    "",
                ]
            )

    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return path
