"""Rotate AI product review topics — no horror scare-pillar logic."""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone

from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.niche import DEFAULT_TOPICS, NICHE_NAME

_STATE_KEY = "invideo_product_index"


def next_product_topic(store: MemoryStore) -> str:
    """Pick next product topic from the locked AI review pool."""
    raw = store.get_channel_state(_STATE_KEY)
    index = int(raw) if raw and raw.isdigit() else 0

    recent = {d.topic.lower() for d in store.list_drafts(limit=20)}
    pool = list(DEFAULT_TOPICS)
    random.shuffle(pool)

    chosen = pool[index % len(pool)]
    for _ in range(len(pool) * 2):
        if chosen.lower() not in recent:
            break
        index += 1
        chosen = pool[index % len(pool)]

    store.set_channel_state(_STATE_KEY, str(index + 1))
    store.set_channel_state("niche_version", "ai_product_reviews_v1")
    store.set_channel_state(
        "last_topic_pick",
        json.dumps(
            {
                "topic": chosen,
                "niche": NICHE_NAME,
                "backend": "invideo",
                "at": datetime.now(timezone.utc).isoformat(),
            }
        ),
    )
    return chosen


def product_name_from_topic(topic: str) -> str:
    for sep in ("—", " - ", " – "):
        if sep in topic:
            return topic.split(sep, 1)[0].strip()
    return topic.strip()
