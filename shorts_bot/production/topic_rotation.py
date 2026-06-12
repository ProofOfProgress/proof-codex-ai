"""Daily topic rotation — Don't Blink horror; skip recent topics and scare pillars."""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone

from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.niche import DEFAULT_TOPICS, NICHE_NAME
from shorts_bot.production.scare_pillar import pillar_label, scare_pillar_for_topic


def _state_path() -> str:
    return "daily_topic_index"


def _recent_pillars(store: MemoryStore) -> set[str]:
    pillars: set[str] = set()
    try:
        from shorts_bot.config import settings
        from shorts_bot.memory.extensions import MemoryExtensions

        mem = MemoryExtensions(MemoryStore(settings.database_path))
        for row in mem.recent_upload_scripts(limit=6):
            pillars.add(scare_pillar_for_topic(row.get("topic", "")))
    except Exception:
        pass
    for d in store.list_drafts(limit=10):
        if d.status in ("approved", "published"):
            pillars.add(scare_pillar_for_topic(d.topic))
    return pillars


def next_topic(store: MemoryStore) -> str:
    """Pick next topic, rotating pool; skip recent topics and uploaded scare pillars."""
    raw = store.get_channel_state(_state_path())
    index = int(raw) if raw and raw.isdigit() else 0

    recent_topics = {d.topic.lower() for d in store.list_drafts(limit=14)}
    used_pillars = _recent_pillars(store)
    pool = list(DEFAULT_TOPICS)
    random.shuffle(pool)

    chosen = pool[index % len(pool)]
    for _ in range(len(pool) * 2):
        pillar = scare_pillar_for_topic(chosen)
        if chosen.lower() not in recent_topics and pillar not in used_pillars:
            break
        index += 1
        chosen = pool[index % len(pool)]

    store.set_channel_state(_state_path(), str(index + 1))
    store.set_channel_state("niche_version", "peripheral_v1")
    pillar = scare_pillar_for_topic(chosen)
    store.set_channel_state(
        "last_topic_pick",
        json.dumps(
            {
                "topic": chosen,
                "niche": NICHE_NAME,
                "scare_pillar": pillar,
                "scare_pillar_label": pillar_label(pillar),
                "at": datetime.now(timezone.utc).isoformat(),
            }
        ),
    )
    return chosen
