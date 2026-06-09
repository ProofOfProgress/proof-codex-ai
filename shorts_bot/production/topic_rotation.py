"""Daily topic rotation — avoid repetitive spam signals at daily cadence."""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore

DEFAULT_TOPICS = [
    "can't sleep at 3am — phone stays dark",
    "Sunday scaries before Monday",
    "can't focus for more than 10 minutes",
    "saying no without a long explanation",
    "overthinking a text you haven't sent",
    "waking up already tired",
    "doom scrolling before bed",
    "comparison spiral on social media",
    "can't start the one task you keep avoiding",
    "anxiety before a normal day",
    "feeling behind everyone else",
    "rest without earning it",
    "brain won't shut up in the shower",
    "snapping at someone you love",
    "can't enjoy downtime without guilt",
    "perfectionism on a small task",
    "lonely in a crowded room",
    "decision fatigue at lunch",
    "can't cry even when you need to",
    "burnout that doesn't look like burnout",
    "replaying an awkward moment",
    "boundary with a friend who vents",
    "morning dread with no clear reason",
    "can't celebrate a small win",
    "feeling numb instead of sad",
    "saying yes when you meant no",
    "caffeine crash at 2pm",
    "can't disconnect after work",
    "shame after procrastinating",
    "need calm before a hard conversation",
]


def _state_path() -> str:
    return "daily_topic_index"


def next_topic(store: MemoryStore) -> str:
    """Pick next topic, rotating through pool and skipping recent drafts."""
    raw = store.get_channel_state(_state_path())
    index = int(raw) if raw and raw.isdigit() else 0

    recent = {d.topic.lower() for d in store.list_drafts(limit=14)}
    pool = list(DEFAULT_TOPICS)
    random.shuffle(pool)

    chosen = pool[index % len(pool)]
    for _ in range(len(pool)):
        if chosen.lower() not in recent:
            break
        index += 1
        chosen = pool[index % len(pool)]

    store.set_channel_state(_state_path(), str(index + 1))
    store.set_channel_state(
        "last_topic_pick",
        json.dumps({"topic": chosen, "at": datetime.now(timezone.utc).isoformat()}),
    )
    return chosen
