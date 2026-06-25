from pathlib import Path

from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.rewards.engine import RewardEngine


def test_reward_includes_breakdown(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "r.db"))
    engine = RewardEngine(mem)
    result = engine.score(
        "test-video",
        {"viewed_vs_swiped_away": 30, "retention_rate": 25, "views": 500, "likes": 5},
    )
    assert result.breakdown
    assert result.verdict == "punish"
    recent = mem.recent_rewards(limit=1)
    assert recent[0].get("breakdown") is not None
