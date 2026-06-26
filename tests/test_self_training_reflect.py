import json
from pathlib import Path

import pytest

from shorts_bot.learning.feedback import learn_from_draft
from shorts_bot.learning.reflect import reflect_after_sync
from shorts_bot.memory.agent_memory import AgentMemoryStore
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.rewards.engine import RewardEngine


@pytest.fixture(autouse=True)
def _self_training_on(monkeypatch):
    from shorts_bot import config

    monkeypatch.setattr(config.settings, "self_training_enabled", True)


def test_upload_snapshots_active_rules(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "t.db"))
    mem.set_training_config("applied:1", "Tighten hook in first 3 seconds")
    mem.record_upload_event(
        draft_id=1,
        topic="sunday couch",
        hook="hook",
        script="script",
        title="Sunday minute",
        video_id="abc123",
    )
    uploads = mem.recent_uploads(hours=1)
    assert uploads
    snap = json.loads(uploads[0]["active_rules_json"])
    assert "Tighten hook" in str(snap.get("applied"))


def test_reflect_after_sync_writes_episode(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "t.db"))
    mem.record_upload_event(
        draft_id=2,
        topic="sunday couch",
        hook="h",
        script="s",
        title="Sunday phone couch",
        video_id="vid99",
    )
    engine = RewardEngine(mem)
    scored = engine.score(
        "Sunday phone couch short",
        {"viewed_vs_swiped_away": 30, "retention_rate": 25, "views": 100},
    )
    result = reflect_after_sync(mem, [scored])
    assert result.episodes_written >= 1
    ctx = mem.applied_training_context()
    assert "REFLECTIONS" in ctx or "RECENT REFLECTIONS" in ctx


def test_draft_feedback_creates_improvement(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "t.db"))
    msg = learn_from_draft(mem, "sleep tips", "too generic", "rejected")
    assert "avoid" in msg.lower() or "Learned" in msg
    imps = mem.list_improvements(status="approved", limit=5)
    assert any("rejected" in i.source for i in imps)


def test_rule_promotion_to_agent_memory(tmp_path: Path):
    store = MemoryStore(tmp_path / "t.db")
    mem = MemoryExtensions(store)
    agent = AgentMemoryStore(store)
    mem.bump_rule_confidence(
        rule_key="applied:0",
        rule_text="Use minute-before hook with concrete protocol",
        positive=True,
        verdict="reward",
    )
    mem.bump_rule_confidence(
        rule_key="applied:0",
        rule_text="Use minute-before hook with concrete protocol",
        positive=True,
        verdict="reward",
    )
    ready = mem.rules_ready_for_promotion(threshold=2)
    assert ready
    from shorts_bot.learning.reflect import reflect_after_sync

    engine = RewardEngine(mem)
    r = engine.score("v", {"viewed_vs_swiped_away": 75, "retention_rate": 65, "views": 500})
    reflect_after_sync(mem, [r], agent_memory_store=agent)
    mems = agent.list_memories(limit=20)
    assert any(m.source == "self_training" for m in mems)
