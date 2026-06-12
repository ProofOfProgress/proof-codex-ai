"""Repair approved horror drafts that drifted to first-person during humanize."""

from __future__ import annotations

import re
from pathlib import Path

from shorts_bot.drafts.generator import DraftGenerator
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.pipeline_integrity import (
    clear_render_artifacts,
    invalidate_downstream_steps,
    write_content_stamp,
)


_FIRST_PERSON_HEAVY = re.compile(r"\b(i|i'm|my|me)\b", re.I)
_SECOND_PERSON = re.compile(r"\b(you|your)\b", re.I)


def script_needs_horror_repair(script: str, hook: str) -> bool:
    combined = f"{hook}\n{script}"
    first = len(_FIRST_PERSON_HEAVY.findall(combined))
    second = len(_SECOND_PERSON.findall(combined))
    return first >= 2 and second < first


def repair_draft_horror_voice(store: MemoryStore, draft_id: int) -> str:
    """Replace first-person drift with offline second-person template; reset pipeline from humanize."""
    draft = store.get_draft(draft_id)
    gen = DraftGenerator(store)
    fixed = gen._generate_offline(draft.topic, draft.help_angle)  # noqa: SLF001

    store.update_draft_content(
        draft_id,
        script=fixed.script,
        hook=fixed.hook,
        help_angle=fixed.help_angle,
    )
    if fixed.visual_beats:
        from shorts_bot.drafts.meta import save_draft_meta

        save_draft_meta(draft_id, visual_beats=fixed.visual_beats)

    from shorts_bot.config import settings

    pack = settings.data_dir / "production" / f"draft_{draft_id}"
    clear_render_artifacts(pack)
    invalidate_downstream_steps(pack, draft_id)
    write_content_stamp(pack, hook=fixed.hook, script=fixed.script)

    return (
        f"Draft #{draft_id} repaired — second-person horror voice restored. "
        f"Cleared checkpoints from humanize onward. Re-run finish_cli."
    )
