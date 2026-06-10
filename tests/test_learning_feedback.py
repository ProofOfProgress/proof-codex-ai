from pathlib import Path

from shorts_bot.learning.feedback import learn_from_draft
from shorts_bot.learning.score_helpers import propose_reward_improvement
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.rewards.engine import RewardEngine
from shorts_bot.training.proposer import ImprovementProposer


def test_reject_draft_learns_immediately(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "t.db"))
    msg = learn_from_draft(mem, "sleep anxiety", "too generic hook", "rejected")
    assert "Learned avoid" in msg
    ctx = mem.applied_training_context()
    assert "too generic hook" in ctx
    assert "AVOID" in ctx


def test_approve_draft_learns_repeat(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "t.db"))
    learn_from_draft(mem, "hard conversation", "first person minute-before angle", "approved")
    ctx = mem.applied_training_context()
    assert "REPEAT" in ctx
    assert "minute-before" in ctx


def test_analytics_upsert(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "t.db"))
    mem.save_analytics("v1", {"views": 100})
    mem.save_analytics("v1", {"views": 200})
    rows = mem.list_analytics(limit=5)
    assert len(rows) == 1
    assert rows[0]["metrics"]["views"] == 200


def test_rejected_improvement_in_avoid_context(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "t.db"))
    imp = mem.create_improvement(
        title="Bad hook idea",
        category="hook",
        description="Use ALL CAPS titles",
        pros=["x"],
        cons=["y"],
    )
    mem.review_improvement(imp.id, approved=False, note="Never do this")
    ctx = mem.applied_training_context()
    assert "rejected proposal" in ctx or "Never do this" in ctx


def test_score_dedup(tmp_path: Path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "t.db"))
    engine = RewardEngine(mem)
    proposer = ImprovementProposer(mem, client=None)
    r = engine.score("v1", {"viewed_vs_swiped_away": 30, "retention_rate": 25})
    first = propose_reward_improvement(mem, proposer, r)
    second = propose_reward_improvement(mem, proposer, r)
    assert first is not None
    assert second is None
