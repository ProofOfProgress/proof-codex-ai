"""Daily topic rotation — niche v2: Don't Blink."""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone

from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.niche import DEFAULT_TOPICS, NICHE_NAME


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
    store.set_channel_state("niche_version", "v2_minute_before")
    store.set_channel_state(
        "last_topic_pick",
        json.dumps(
            {
                "topic": chosen,
                "niche": NICHE_NAME,
                "at": datetime.now(timezone.utc).isoformat(),
            }
        ),
    )
    return chosen
