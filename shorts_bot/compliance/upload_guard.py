"""Block uploads that match inauthentic / spam-farm patterns."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from shorts_bot.compliance.inauthentic_rules import risk_signals_for_script
from shorts_bot.config import settings
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore


@dataclass
class ComplianceReport:
    allowed: bool
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.allowed and not self.warnings:
            return "YPP compliance check passed."
        parts = []
        if self.issues:
            parts.append("BLOCKED: " + "; ".join(self.issues))
        if self.warnings:
            parts.append("Warnings: " + "; ".join(self.warnings))
        return " ".join(parts)


def _token_set(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9']+", text.lower()) if len(w) > 2}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def check_upload_allowed(
    store: MemoryStore,
    memory: MemoryExtensions,
    *,
    draft_id: int,
    topic: str,
    hook: str,
    script: str,
    title: str,
) -> ComplianceReport:
    if not settings.ypp_safe_mode:
        return ComplianceReport(True)

    issues: list[str] = []
    warnings: list[str] = []

    for risk in risk_signals_for_script(script, hook, title):
        if "missing first-person" in risk or "spam-farm" in risk:
            issues.append(risk)
        else:
            warnings.append(risk)

    now = datetime.now(timezone.utc)
    recent = memory.recent_uploads(hours=24)
    if len(recent) >= settings.max_uploads_per_24h:
        issues.append(
            f"max {settings.max_uploads_per_24h} upload(s) per 24h (already {len(recent)}) — spam-farm signal"
        )
    elif recent:
        last = recent[0]
        last_at = datetime.fromisoformat(last["uploaded_at"].replace("Z", "+00:00"))
        if last_at.tzinfo is None:
            last_at = last_at.replace(tzinfo=timezone.utc)
        hours = (now - last_at).total_seconds() / 3600
        if hours < settings.min_hours_between_uploads:
            issues.append(
                f"only {hours:.1f}h since last upload — wait {settings.min_hours_between_uploads}h minimum"
            )

    topic_key = topic.strip().lower()
    if memory.topic_uploaded_within_days(topic_key, days=settings.topic_cooldown_days):
        issues.append(f"topic uploaded within last {settings.topic_cooldown_days} days")

    hook_key = hook.strip().lower()[:120]
    if memory.hook_uploaded_within_days(hook_key, days=settings.hook_cooldown_days):
        issues.append(f"hook too similar to recent upload (within {settings.hook_cooldown_days} days)")

    script_tokens = _token_set(script)
    for prev in memory.recent_upload_scripts(limit=5):
        if prev.get("draft_id") == draft_id:
            continue
        overlap = _jaccard(script_tokens, _token_set(prev.get("script", "")))
        if overlap >= settings.max_script_overlap_ratio:
            issues.append(
                f"script {overlap:.0%} similar to draft #{prev.get('draft_id')} — template repetition"
            )
            break

    for d in store.list_drafts(limit=20):
        if d.id == draft_id:
            continue
        if d.topic.strip().lower() == topic_key and d.status == "approved":
            warnings.append(f"same topic in draft #{d.id} — ensure script is meaningfully different")

    allowed = len(issues) == 0
    return ComplianceReport(allowed=allowed, issues=issues, warnings=warnings)


def record_upload(
    memory: MemoryExtensions,
    *,
    draft_id: int,
    topic: str,
    hook: str,
    script: str,
    title: str,
    video_id: str,
    extra_snapshot: dict | None = None,
) -> None:
    snapshot = memory.active_rules_snapshot()
    if extra_snapshot:
        snapshot.update(extra_snapshot)
    memory.record_upload_event(
        draft_id=draft_id,
        topic=topic,
        hook=hook,
        script=script,
        title=title,
        video_id=video_id,
        active_rules_json=json.dumps(snapshot),
    )
