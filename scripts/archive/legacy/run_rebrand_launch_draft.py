#!/usr/bin/env python3
"""Bootstrap draft #3 — first post-rebrand Peripheral mind-fuck episode."""

from __future__ import annotations

from shorts_bot.config import settings
from shorts_bot.drafts.meta import save_draft_meta
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.pipeline import finish_draft_pipeline

TOPIC = "you filmed the sign to prove it wasn't real — the playback showed you already watching"

HOOK = "The playback timestamp was yesterday — before you ever pressed record."

SCRIPT = (
    "You filmed the village sign to prove it wasn't real. "
    "The playback opened on yesterday's fog, before you pressed record. "
    "Your name was already carved in the wood. "
    "The baker crossed herself and walked inside. "
    "You told yourself the file was corrupted, a bad timestamp. "
    "The doctor said your throat was fine, you hadn't swallowed in six days. "
    "The mist held still — you told yourself that meant safety. "
    "You zoomed the frame. The sign wasn't naming you. It was counting down. "
    "Today reads zero. The wood splits, and the eye in the center turns to meet yours."
)

HELP = (
    "Black Mirror village curse — playback trap twist; "
    "sign counts down days left; Peripheral eye sting on zero."
)

VISUAL_BEATS = [
    "Fog-grey village square at dusk, crooked signpost with wrong symbol on barn wood, cold clinical wide",
    "Handheld VHS camcorder POV filming the sign, REC overlay, film grain, no smartphone",
    "Small CRT in baker window plays back footage, timestamp yesterday, villagers silhouettes turn away",
    "Macro carved name in rotting wood, fresh splinters, cold blue light",
    "Baker crosses herself, door slams, empty cobblestone, no faces toward camera",
    "Doctor's scale and empty bowl on table, implied sickness, underexposed clinic",
    "False calm: mist rolls over empty square, sign still in distance, slow drift",
    "Sign wood splits, countdown reads zero, macro white eye opens in center and lunges full frame",
]


def _draft_exists(store: MemoryStore, draft_id: int) -> bool:
    try:
        store.get_draft(draft_id)
        return True
    except KeyError:
        return False


def main() -> None:
    store = MemoryStore(settings.database_path)
    existing = store.get_draft(3) if _draft_exists(store, 3) else None
    if existing and existing.topic == TOPIC:
        draft = existing
        store.update_draft_content(
            draft.id,
            hook=HOOK,
            script=SCRIPT,
            help_angle=HELP,
        )
        print(f"Using draft #{draft.id} (updated script)")
    else:
        draft = store.save_draft(
            topic=TOPIC,
            script=SCRIPT,
            hook=HOOK,
            help_angle=HELP,
            quality_notes="Rebrand launch — Black Mirror village curse mind-fuck (manual script)",
        )
        save_draft_meta(draft.id, visual_beats=VISUAL_BEATS)
        print(f"Draft #{draft.id} created")
    if existing is None or existing.status != "approved":
        store.review_draft(draft.id, "approved", "Rebrand launch — auto-approved")
    save_draft_meta(draft.id, visual_beats=VISUAL_BEATS)
    result = finish_draft_pipeline(store, draft.id, upload_youtube=True, resume=False)
    for msg in result.messages:
        print(msg)
    if result.upload_url:
        print(f"PUBLISHED: {result.upload_url}")
    elif result.video_path:
        print(f"RENDERED: {result.video_path}")
    else:
        print("Pipeline finished without video or upload URL")


if __name__ == "__main__":
    main()
