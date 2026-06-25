from pathlib import Path

from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.rewards.engine import RewardEngine


def test_reward_punish_weak_swipe(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "t.db"))
    engine = RewardEngine(mem)
    r = engine.score("v1", {"viewed_vs_swiped_away": 35, "retention_rate": 30, "views": 1000})
    assert r.verdict == "punish"
    assert r.score < 0


def test_reward_strong_video(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "t.db"))
    engine = RewardEngine(mem)
    r = engine.score("v1", {"viewed_vs_swiped_away": 75, "retention_rate": 65, "views": 5000, "likes": 400})
    assert r.verdict == "reward"
    assert r.score > 0


def test_improvement_from_punish(tmp_path: Path):
    from shorts_bot.training.proposer import ImprovementProposer

    mem = MemoryExtensions(MemoryStore(tmp_path / "t.db"))
    engine = RewardEngine(mem)
    r = engine.score("bad", {"viewed_vs_swiped_away": 30, "retention_rate": 25})
    imp = ImprovementProposer(mem, client=None).propose_from_reward(r)
    assert imp is not None
    assert imp.pros and imp.cons
    assert imp.status == "pending"
