"""Structured product queue — Jenny hooks + strength/weakness for daily rotation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.production.hooks import migrate_verdict_hint

QUEUE_PATH = Path("data/product_queue.json")


@dataclass
class ProductQueueItem:
    id: int
    product: str
    topic: str
    hook: str
    strength_hint: str = ""
    weakness_hint: str = ""
    verdict_hint: str = ""  # legacy — migrated to hints when missing

    def resolved_hints(self) -> tuple[str, str]:
        """Strength/weakness for brief — explicit fields or legacy verdict migration."""
        s, w = self.strength_hint.strip(), self.weakness_hint.strip()
        if s or w:
            return s, w
        return migrate_verdict_hint(self.verdict_hint)


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
                strength_hint=str(row.get("strength_hint") or ""),
                weakness_hint=str(row.get("weakness_hint") or ""),
                verdict_hint=str(row.get("verdict_hint") or ""),
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
    lines = ["Product queue (Ms. Byte — strength/weakness):"]
    for item in load_product_queue()[:limit]:
        hook_preview = item.hook[:55] + "…" if len(item.hook) > 55 else item.hook
        lines.append(f"  #{item.id} {item.product} — {hook_preview}")
    return "\n".join(lines)
