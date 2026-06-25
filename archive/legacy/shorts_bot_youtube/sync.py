from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import _utc_now
from shorts_bot.rewards.engine import RewardEngine, RewardResult
from shorts_bot.training.proposer import ImprovementProposer
from shorts_bot.youtube.analytics_client import enrich_titles, fetch_video_metrics
from shorts_bot.youtube.google_auth import auth_status

MAX_IMPROVEMENTS_PER_SYNC = 3


@dataclass
class SyncResult:
    ok: bool
    message: str
    videos_scored: int = 0
    improvements_created: int = 0
    rewards: list[dict[str, Any]] | None = None
    scored_results: list[RewardResult] | None = None


class AnalyticsSync:
    def __init__(self, memory: MemoryExtensions, proposer: ImprovementProposer) -> None:
        self.memory = memory
        self.engine = RewardEngine(memory)
        self.proposer = proposer

    def run(self, *, days: int = 28, max_videos: int = 15) -> SyncResult:
        status = auth_status()
        if not status["ready"]:
            if not status["credentials_configured"]:
                return SyncResult(
                    ok=False,
                    message="Add Google API keys to .env — see docs/TOMORROW.md",
                )
            return SyncResult(
                ok=False,
                message="Run once: python3 -m shorts_bot.youtube.auth_cli",
            )

        try:
            metrics = fetch_video_metrics(days=days, max_videos=max_videos)
            metrics = enrich_titles(metrics)
        except Exception as exc:  # noqa: BLE001
            return SyncResult(ok=False, message=f"Analytics sync failed: {exc}")

        if not metrics:
            return SyncResult(
                ok=True,
                message="No video data yet. Upload a Short first.",
                videos_scored=0,
            )

        history = self.memory.list_analytics(limit=50)
        from shorts_bot.youtube.analytics_merge import find_existing_for_video, merge_metrics

        rewards: list[dict[str, Any]] = []
        scored: list[RewardResult] = []

        for m in metrics:
            existing = find_existing_for_video(
                history, str(m.get("video_id") or ""), str(m.get("video_label") or "")
            )
            merged = merge_metrics(existing, m)
            label = str(merged.get("video_label") or m["video_label"])
            result = self.engine.score(label, merged)
            scored.append(result)
            rewards.append(
                {
                    "video": label,
                    "title": merged.get("title", label),
                    "verdict": result.verdict,
                    "score": result.score,
                    "reason": result.reason,
                }
            )

        improvements_created = self._propose_improvements(scored)

        self.memory.set_training_config("last_analytics_sync", _utc_now())

        return SyncResult(
            ok=True,
            message=(
                f"Synced {len(metrics)} videos (last {days}d window). "
                "Swipe-away is Studio-only — not from API."
            ),
            videos_scored=len(metrics),
            improvements_created=improvements_created,
            rewards=rewards,
            scored_results=scored,
        )

    def _pending_sources(self) -> set[str]:
        return {p.source for p in self.memory.list_improvements(status="pending", limit=100) if p.source}

    def _propose_improvements(self, scored: list[RewardResult]) -> int:
        """Cap proposals so sign-off stays easy (max 3 per sync)."""
        pending = self._pending_sources()
        punishes = sorted((r for r in scored if r.verdict == "punish"), key=lambda r: r.score)
        wins = sorted((r for r in scored if r.verdict == "reward"), key=lambda r: r.score, reverse=True)
        candidates = punishes[:2] + wins[:1]

        from shorts_bot.learning.score_helpers import propose_reward_improvement

        created = 0
        for result in candidates:
            source = f"reward:{result.verdict}:{result.video_label}"
            if source in pending:
                continue
            if propose_reward_improvement(self.memory, self.proposer, result):
                created += 1
                pending.add(source)
            if created >= MAX_IMPROVEMENTS_PER_SYNC:
                break

        if created == 0 and punishes:
            worst = punishes[0]
            source = f"reward:punish:{worst.video_label}"
            if source not in pending and self.proposer.propose_from_reward(worst):
                created += 1

        return created
