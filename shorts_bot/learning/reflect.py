"""Autonomous self-training — experience → reflection → consolidation (no weight updates).

Inspired by reflective memory (Memento/SRDP), dual-process agents (DPA), and ERL-style
experience–reflection–consolidation loops. See docs/AUTONOMOUS_SELF_TRAINING_RESEARCH.md.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from shorts_bot.config import settings
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.rewards.engine import RewardResult


@dataclass
class ReflectResult:
    episodes_written: int = 0
    rules_validated: int = 0
    rules_demoted: int = 0
    rules_promoted_to_memory: int = 0
    reflections: list[str] | None = None

    def summary(self) -> str:
        parts = []
        if self.episodes_written:
            parts.append(f"{self.episodes_written} episode(s) consolidated")
        if self.rules_validated:
            parts.append(f"{self.rules_validated} rule(s) validated")
        if self.rules_demoted:
            parts.append(f"{self.rules_demoted} rule(s) demoted")
        if self.rules_promoted_to_memory:
            parts.append(f"{self.rules_promoted_to_memory} promoted to agent memory")
        return "; ".join(parts) if parts else "No new reflections"


def _youtube_id_from_label(label: str) -> str | None:
    import re

    m = re.search(r"(?<![\w-])([a-zA-Z0-9_-]{11})(?![\w-])", label)
    return m.group(1) if m else None


def _match_upload(
    memory: MemoryExtensions,
    video_label: str,
    *,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    label = video_label.lower().strip()
    video_id = (metrics or {}).get("video_id") or _youtube_id_from_label(video_label)
    if video_id:
        video_id = str(video_id).lower()
    for row in memory.recent_uploads(hours=24 * 90):
        vid = (row.get("video_id") or "").lower()
        if video_id and vid == video_id:
            return row
        title = (row.get("title") or "").lower()
        topic = (row.get("topic") or "").lower()
        if vid and vid in label:
            return row
        if title and (title in label or label in title):
            return row
        if topic and topic[:40] in label:
            return row
    return None


def _offline_reflection(result: RewardResult, upload: dict[str, Any] | None) -> str:
    lines = [
        f"Outcome: {result.verdict} ({result.score:+.2f}) — {result.reason[:200]}",
        f"Diagnosis: {result.diagnosis[:300]}",
    ]
    if upload:
        lines.append(f"Upload topic: {(upload.get('topic') or '')[:100]}")
    if result.verdict == "punish":
        lines.append(
            "Reflection: Hook or pacing likely failed — avoid repeating this angle; "
            "check APPROVED RULES before next draft."
        )
    elif result.verdict == "reward":
        lines.append(
            "Reflection: Pattern worked — bias next draft toward this hook style and beat pacing."
        )
    else:
        lines.append("Reflection: Neutral signal — gather more data before changing rules.")
    return "\n".join(lines)


def _rule_keys_from_snapshot(snapshot: dict[str, Any]) -> list[tuple[str, str]]:
    """(rule_key, rule_text) pairs from upload-time snapshot."""
    pairs: list[tuple[str, str]] = []
    for i, text in enumerate(snapshot.get("applied") or []):
        if text:
            pairs.append((f"applied:{i}", str(text)[:400]))
    return pairs


def reflect_after_sync(
    memory: MemoryExtensions,
    scored: list[RewardResult],
    *,
    agent_memory_store: Any | None = None,
) -> ReflectResult:
    """
    Slow loop (System 2): attribute outcomes to active rules, write episodes, promote winners.

    Runs after analytics sync when SELF_TRAINING_ENABLED=true.
    """
    if not settings.self_training_enabled:
        return ReflectResult()

    result = ReflectResult(reflections=[])
    threshold = settings.self_training_promote_threshold

    for reward in scored:
        if reward.verdict == "neutral":
            continue

        upload = _match_upload(memory, reward.video_label, metrics=reward.metrics)
        snapshot: dict[str, Any] = {}
        if upload and upload.get("active_rules_json"):
            try:
                snapshot = json.loads(upload["active_rules_json"])
            except json.JSONDecodeError:
                snapshot = {}

        reflection = _offline_reflection(reward, upload)
        memory.record_learning_episode(
            episode_type="analytics_sync",
            video_label=reward.video_label,
            verdict=reward.verdict,
            score=reward.score,
            reflection=reflection,
            active_rules_json=json.dumps(snapshot) if snapshot else None,
        )
        result.episodes_written += 1
        if result.reflections is not None:
            result.reflections.append(reflection[:280])

        for rule_key, rule_text in _rule_keys_from_snapshot(snapshot):
            conf = memory.bump_rule_confidence(
                rule_key=rule_key,
                rule_text=rule_text,
                positive=reward.verdict == "reward",
                verdict=reward.verdict,
            )
            result.rules_validated += 1
            if conf.punish_hits >= 2 and conf.confidence < 0.35:
                memory.demote_rule(rule_key, reason=f"Low confidence after {conf.punish_hits} punishes")
                result.rules_demoted += 1

    if agent_memory_store is not None:
        for row in memory.rules_ready_for_promotion(threshold=threshold):
            title = f"Learned: {row['rule_text'][:50]}"
            existing = agent_memory_store.find_by_title_prefix(title[:40])
            if existing:
                continue
            agent_memory_store.add_memory(
                category="operating_rule",
                title=title,
                content=row["rule_text"][:800],
                source="self_training",
                pinned=False,
            )
            memory.mark_rule_promoted(row["rule_key"])
            result.rules_promoted_to_memory += 1

    return result


def consolidate_draft_feedback(
    memory: MemoryExtensions,
    *,
    topic: str,
    reason: str,
    decision: str,
) -> str:
    """Write draft decision into episodic memory for future retrieval."""
    reflection = (
        f"Draft {decision} on «{topic[:60]}»: {reason[:300]}. "
        f"{'Avoid similar patterns.' if decision == 'rejected' else 'Repeat when relevant.'}"
    )
    memory.record_learning_episode(
        episode_type=f"draft_{decision}",
        video_label=topic[:120],
        verdict=decision,
        score=1.0 if decision == "approved" else -1.0,
        reflection=reflection,
        active_rules_json=json.dumps(memory.active_rules_snapshot()),
    )
    return reflection
