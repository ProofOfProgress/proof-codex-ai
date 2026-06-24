"""Rotate AI product review topics — structured queue + fallback pool."""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone

from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.niche import DEFAULT_TOPICS, NICHE_NAME
from shorts_bot.production.product_queue import next_queue_item

_STATE_KEY = "invideo_product_index"
_PENDING_QUEUE_KEY = "pending_queue_item"


def next_product_topic(store: MemoryStore) -> str:
    """Pick next product topic — prefers data/product_queue.json."""
    item = next_queue_item(store)
    if item:
        store.set_channel_state(
            _PENDING_QUEUE_KEY,
            json.dumps(
                {
                    "product": item.product,
                    "topic": item.topic,
                    "hook": item.hook,
                    "strength_hint": item.strength_hint,
                    "weakness_hint": item.weakness_hint,
                    "verdict_hint": item.verdict_hint,
                }
            ),
        )
        store.set_channel_state("niche_version", "tiktok_shop_fix_it_fast_v1")
        store.set_channel_state(
            "last_topic_pick",
            json.dumps(
                {
                    "topic": item.topic,
                    "product": item.product,
                    "niche": NICHE_NAME,
                    "backend": "invideo",
                    "queue_id": item.id,
                    "at": datetime.now(timezone.utc).isoformat(),
                }
            ),
        )
        return item.topic

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


def consume_pending_queue_item(store: MemoryStore) -> dict | None:
    raw = store.get_channel_state(_PENDING_QUEUE_KEY)
    if not raw:
        return None
    store.set_channel_state(_PENDING_QUEUE_KEY, "")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def product_name_from_topic(topic: str) -> str:
    for sep in ("—", " - ", " – "):
        if sep in topic:
            return topic.split(sep, 1)[0].strip()
    return topic.strip()
