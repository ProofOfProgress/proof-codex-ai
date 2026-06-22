from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shorts_bot.memory.extensions import MemoryExtensions, RewardEvent
from shorts_bot.memory.store import _utc_now


@dataclass
class RewardResult:
    video_label: str
    score: float
    verdict: str
    reason: str
    metrics: dict[str, Any]
    diagnosis: str
    breakdown: list[dict[str, Any]] = field(default_factory=list)

    @property
    def is_reward(self) -> bool:
        return self.verdict == "reward"

    @property
    def is_punish(self) -> bool:
        return self.verdict == "punish"


class RewardEngine:
    """
    Scores Short performance vs Jenny course benchmarks and channel history.

    Key metrics (from course file 09):
    - viewed_vs_swiped_away (target ~70%+, higher for entertainment)
    - retention_rate
    - engagement (likes, comments)
    """

    def __init__(self, memory: MemoryExtensions) -> None:
        self.memory = memory

    def score(self, video_label: str, metrics: dict[str, Any]) -> RewardResult:
        self.memory.save_analytics(video_label, metrics)

        swipe = float(metrics.get("viewed_vs_swiped_away", metrics.get("swipe_away_inverse", 0)) or 0)
        swipe_source = str(metrics.get("swipe_source", "manual" if swipe else "unavailable"))
        use_swipe = swipe > 0 and swipe_source not in ("unavailable", "estimated")
        retention_src = str(metrics.get("retention_source") or "")
        avg_watch = float(
            metrics.get("average_view_percentage", metrics.get("retention_rate", 0)) or 0
        )
        studio_retention = float(metrics.get("retention_rate", 0) or 0) if retention_src == "studio" else 0.0
        retention = studio_retention if studio_retention > 0 else avg_watch
        api_only = not use_swipe and swipe_source == "unavailable"
        views = int(metrics.get("views", 0))
        likes = int(metrics.get("likes", 0))

        history = self.memory.list_analytics(limit=10)
        baseline = self._baseline(history, exclude_label=video_label)

        score = 0.0
        reasons: list[str] = []
        breakdown: list[dict[str, Any]] = []

        def bump(delta: float, factor: str, note: str) -> None:
            nonlocal score
            score += delta
            breakdown.append({"factor": factor, "delta": round(delta, 3), "note": note})
            reasons.append(note)

        if use_swipe:
            if swipe >= 70:
                bump(0.35, "swipe_away", f"Strong swipe-away survival ({swipe:.0f}% viewed)")
            elif swipe < 50:
                bump(-0.4, "swipe_away", f"Weak hook/idea — only {swipe:.0f}% viewed vs swiped")
            else:
                breakdown.append({"factor": "swipe_away", "delta": 0, "note": f"Mid swipe-away ({swipe:.0f}%)"})
                reasons.append(f"Mid swipe-away ({swipe:.0f}%)")
        elif retention <= 0 and views <= 0:
            reasons.append(
                "Insufficient metrics — API sync has no swipe-away; add Studio numbers via score API"
            )
        elif api_only and retention > 0:
            reasons.append(
                f"API avg watch {retention:.0f}% (last window) — not Studio retention graph; swipe N/A"
            )

        if retention > 0:
            ret_weight = 0.15 if api_only and not use_swipe else 0.35
            if retention >= 60:
                bump(ret_weight, "retention", f"Good avg watch ({retention:.0f}%)")
            elif retention < 40:
                bump(-ret_weight, "retention", f"Low avg watch ({retention:.0f}%) — verify in Studio")
            else:
                breakdown.append({"factor": "retention", "delta": 0, "note": f"Mid avg watch ({retention:.0f}%)"})
                reasons.append(f"Mid avg watch ({retention:.0f}%)")

        if baseline and use_swipe:
            b_swipe = baseline.get("viewed_vs_swiped_away", 0)
            b_ret = baseline.get("retention_rate", 0)
            if swipe and b_swipe and swipe > b_swipe + 5:
                bump(0.15, "channel_avg", "Beat your channel average on swipe-away")
            elif swipe and b_swipe and swipe < b_swipe - 5:
                bump(-0.15, "channel_avg", "Worse than your channel average on swipe-away")
            if retention and b_ret and retention > b_ret + 5:
                bump(0.15, "channel_avg", "Beat your channel average on retention")
            elif retention and b_ret and retention < b_ret - 5:
                bump(-0.15, "channel_avg", "Worse than your channel average on retention")
        elif baseline:
            b_ret = baseline.get("retention_rate", 0)
            if retention and b_ret and retention > b_ret + 5:
                bump(0.15, "channel_avg", "Beat your channel average on retention")
            elif retention and b_ret and retention < b_ret - 5:
                bump(-0.15, "channel_avg", "Worse than your channel average on retention")

        if views > 0 and likes / max(views, 1) > 0.05:
            bump(0.1, "engagement", "Solid like ratio")

        score = max(-1.0, min(1.0, score))

        if score >= 0.25:
            verdict = "reward"
        elif score <= -0.25:
            verdict = "punish"
        else:
            verdict = "neutral"

        # API-only sync should not auto-punish hard without swipe data
        if api_only and not use_swipe and verdict == "punish" and abs(score) < 0.4:
            verdict = "neutral"
            reasons.append("Neutral — need Studio swipe-away before strong punish/reward")

        diagnosis = self._diagnose(swipe, retention, verdict, use_swipe=use_swipe)
        reason = "; ".join(reasons) if reasons else "Insufficient metrics"

        result = RewardResult(
            video_label=video_label,
            score=round(score, 3),
            verdict=verdict,
            reason=reason,
            metrics=metrics,
            diagnosis=diagnosis,
            breakdown=breakdown,
        )

        self.memory.save_reward(
            RewardEvent(
                id=0,
                video_label=video_label,
                score=result.score,
                verdict=verdict,
                reason=reason,
                metrics=metrics,
                created_at=_utc_now(),
                breakdown=breakdown,
            )
        )
        return result

    @staticmethod
    def _baseline(history: list[dict[str, Any]], exclude_label: str) -> dict[str, float]:
        vals_swipe: list[float] = []
        vals_ret: list[float] = []
        for row in history:
            if row["video_label"] == exclude_label:
                continue
            m = row["metrics"]
            s = m.get("viewed_vs_swiped_away", m.get("swipe_away_inverse"))
            r = m.get("retention_rate", m.get("average_view_percentage"))
            if s:
                vals_swipe.append(float(s))
            if r:
                vals_ret.append(float(r))
        out: dict[str, float] = {}
        if vals_swipe:
            out["viewed_vs_swiped_away"] = sum(vals_swipe) / len(vals_swipe)
        if vals_ret:
            out["retention_rate"] = sum(vals_ret) / len(vals_ret)
        return out

    @staticmethod
    def _diagnose(swipe: float, retention: float, verdict: str, *, use_swipe: bool = True) -> str:
        if verdict == "punish":
            if use_swipe and swipe and swipe < 50:
                return "Start upstream: hook and core idea likely failed (course lever 02)."
            if retention and retention < 40:
                return "Middle/payoff issue — check script pacing and retention beats (lever 06)."
            return "Underperformed vs benchmarks — review decision ladder (lever 01)."
        if verdict == "reward":
            return "Repeat strengths from this video in the next draft."
        return "Mixed signals — run post-mortem before changing strategy."
