"""Structured product queue — hooks + verdicts for daily rotation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings

QUEUE_PATH = Path("data/product_queue.json")


@dataclass
class ProductQueueItem:
    id: int
    product: str
    topic: str
    hook: str
    verdict_hint: str


def load_product_queue(path: Path | None = None) -> list[ProductQueueItem]:
    p = path or QUEUE_PATH
    if not p.is_file():
        return []
    raw = json.loads(p.read_text(encoding="utf-8"))
    out: list[ProductQueueItem] = []
    for row in raw:
        out.append(
            ProductQueueItem(
                id=int(row["id"]),
                product=str(row["product"]),
                topic=str(row["topic"]),
                hook=str(row.get("hook") or ""),
                verdict_hint=str(row.get("verdict_hint") or "Pay, Skip, or Wait"),
            )
        )
    return out


def next_queue_item(store, *, state_key: str = "product_queue_index") -> ProductQueueItem | None:
    queue = load_product_queue()
    if not queue:
        return None
    raw = store.get_channel_state(state_key)
    index = int(raw) if raw and raw.isdigit() else 0
    recent = {d.topic.lower() for d in store.list_drafts(limit=30)}
    for offset in range(len(queue)):
        item = queue[(index + offset) % len(queue)]
        if item.topic.lower() not in recent:
            store.set_channel_state(state_key, str(index + offset + 1))
            return item
    item = queue[index % len(queue)]
    store.set_channel_state(state_key, str(index + 1))
    return item


def queue_item_by_product(product: str) -> ProductQueueItem | None:
    key = product.strip().lower()
    for item in load_product_queue():
        if item.product.lower() == key or key in item.topic.lower():
            return item
    return None


def queue_summary(limit: int = 15) -> str:
    lines = ["Product queue (Pay/Skip/Wait):"]
    for item in load_product_queue()[:limit]:
        lines.append(f"  #{item.id} {item.product} — {item.verdict_hint[:50]}")
    return "\n".join(lines)
