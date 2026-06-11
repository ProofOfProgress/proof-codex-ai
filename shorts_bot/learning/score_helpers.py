"""Shared reward → improvement proposal with dedup (sync + manual score)."""

from __future__ import annotations

from shorts_bot.memory.extensions import Improvement, MemoryExtensions
from shorts_bot.rewards.engine import RewardResult
from shorts_bot.training.proposer import ImprovementProposer


def propose_reward_improvement(
    memory: MemoryExtensions,
    proposer: ImprovementProposer,
    result: RewardResult,
) -> Improvement | None:
    if result.verdict == "neutral":
        return None
    source = f"reward:{result.verdict}:{result.video_label}"
    pending = {
        p.source
        for p in memory.list_improvements(status="pending", limit=100)
        if p.source
    }
    if source in pending:
        return None
    return proposer.propose_from_reward(result)
