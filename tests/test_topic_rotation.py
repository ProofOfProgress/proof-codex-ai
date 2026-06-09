from pathlib import Path

from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.topic_rotation import DEFAULT_TOPICS, next_topic


def test_next_topic_rotates(tmp_path: Path):
    store = MemoryStore(tmp_path / "t.db")
    t1 = next_topic(store)
    t2 = next_topic(store)
    assert t1 in DEFAULT_TOPICS
    assert t2 in DEFAULT_TOPICS
