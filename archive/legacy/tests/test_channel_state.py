from pathlib import Path

from shorts_bot.memory.store import MemoryStore


def test_mark_channel_ready(tmp_path: Path):
    store = MemoryStore(tmp_path / "t.db")
    store.mark_channel_ready(channel_name="My Channel", note="user set up")
    summary = store.channel_summary()
    assert summary["ready"] == "true"
    assert summary["channel_name"] == "My Channel"
