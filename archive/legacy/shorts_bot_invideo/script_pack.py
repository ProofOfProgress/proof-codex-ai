"""Prepare draft script files for InVideo (copy-paste or MCP)."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore


def draft_pack_dir(draft_id: int) -> Path:
    return settings.data_dir / "production" / f"draft_{draft_id}"


def write_script_pack(
    draft_id: int,
    *,
    script: str | None = None,
    topic: str | None = None,
    hook: str | None = None,
) -> Path:
    """Write invideo_script.txt + README into draft pack folder."""
    store = MemoryStore(settings.database_path)
    draft = store.get_draft(draft_id)
    script = (script or draft.script).strip()
    topic = (topic or draft.topic).strip()
    hook = (hook or draft.hook or "").strip()

    pack = draft_pack_dir(draft_id)
    pack.mkdir(parents=True, exist_ok=True)

    script_path = pack / "invideo_script.txt"
    script_path.write_text(script + "\n", encoding="utf-8")

    readme = pack / "INVIDEO_README.txt"
    readme.write_text(
        f"Draft #{draft_id}: {topic}\n\n"
        f"Hook: {hook}\n\n"
        "Agent path:\n"
        f"  python3 -m shorts_bot.invideo.generate_cli --draft-id {draft_id}\n\n"
        "Manual path:\n"
        "  1. Open https://ai.invideo.io (logged in)\n"
        "  2. Create New → paste invideo_script.txt\n"
        "  3. Use your AI twin + 9:16 Shorts + captions\n"
        "  4. Export MP4 → save as final_short.mp4 in this folder\n"
        "  5. Tell agent: upload draft {draft_id}\n".format(draft_id=draft_id),
        encoding="utf-8",
    )
    return script_path
