"""Select best Short drafts for long-form compilation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.pack_health import assess_pack_health
from shorts_bot.production.short_video_resolver import resolve_final_short_video


@dataclass
class DraftCandidate:
    draft_id: int
    topic: str
    hook: str
    video_path: Path
    duration_seconds: float
    score: float
    uploaded: bool = False
    video_id: str = ""
    pack_healthy: bool = False
    reasons: list[str] = field(default_factory=list)


def _uploaded_draft_ids(mem: MemoryExtensions) -> dict[int, str]:
    """Map draft_id → video_id for non-voided uploads."""
    out: dict[int, str] = {}
    for row in mem.recent_upload_scripts(limit=50, include_voided=False):
        did = int(row.get("draft_id") or 0)
        if did and did not in out:
            out[did] = str(row.get("video_id") or "")
    return out


def _probe_duration_safe(path: Path) -> float:
    try:
        from shorts_bot.production.long_form_render import probe_duration

        return probe_duration(path)
    except Exception:
        return 0.0


def score_draft_candidate(
    *,
    draft_id: int,
    topic: str,
    hook: str,
    video_path: Path,
    uploaded: bool,
    pack_healthy: bool,
) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    if video_path.is_file():
        score += 40.0
        reasons.append("has rendered Short")
        dur = _probe_duration_safe(video_path)
        if 22.0 <= dur <= 45.0:
            score += 15.0
            reasons.append(f"duration in Short band ({dur:.1f}s)")
        elif dur > 0:
            score += 5.0
    else:
        reasons.append("missing final_short MP4")
        return score, reasons

    if pack_healthy:
        score += 20.0
        reasons.append("pack health OK")
    else:
        reasons.append("pack health issues")

    if uploaded:
        score += 25.0
        reasons.append("published on channel (retention signal TBD)")

    if hook and len(hook) >= 12:
        score += 5.0
        reasons.append("strong hook line")

    return score, reasons


def list_draft_candidates(
    *,
    limit: int = 10,
    require_video: bool = True,
) -> list[DraftCandidate]:
    store = MemoryStore(settings.database_path)
    mem = MemoryExtensions(store)
    uploaded = _uploaded_draft_ids(mem)

    candidates: list[DraftCandidate] = []
    for draft in store.list_drafts(limit=limit * 3):
        pack_dir = settings.data_dir / "production" / f"draft_{draft.id}"
        video = resolve_final_short_video(pack_dir)
        if require_video and (video is None or not video.is_file()):
            continue

        health = assess_pack_health(pack_dir, draft_id=draft.id)
        is_up = draft.id in uploaded
        score, reasons = score_draft_candidate(
            draft_id=draft.id,
            topic=draft.topic,
            hook=draft.hook,
            video_path=video or Path(),
            uploaded=is_up,
            pack_healthy=health.ready_to_render,
        )
        candidates.append(
            DraftCandidate(
                draft_id=draft.id,
                topic=draft.topic,
                hook=draft.hook,
                video_path=video or Path(),
                duration_seconds=_probe_duration_safe(video) if video else 0.0,
                score=score,
                uploaded=is_up,
                video_id=uploaded.get(draft.id, ""),
                pack_healthy=health.ready_to_render,
                reasons=reasons,
            )
        )

    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates[:limit]


def pick_compilation_drafts(
    *,
    limit: int = 3,
    draft_ids: list[int] | None = None,
) -> list[DraftCandidate]:
    if draft_ids:
        store = MemoryStore(settings.database_path)
        mem = MemoryExtensions(store)
        uploaded = _uploaded_draft_ids(mem)
        picked: list[DraftCandidate] = []
        for did in draft_ids:
            draft = store.get_draft(did)
            pack_dir = settings.data_dir / "production" / f"draft_{did}"
            video = resolve_final_short_video(pack_dir)
            if video is None:
                continue
            health = assess_pack_health(pack_dir, draft_id=did)
            is_up = did in uploaded
            score, reasons = score_draft_candidate(
                draft_id=did,
                topic=draft.topic,
                hook=draft.hook,
                video_path=video,
                uploaded=is_up,
                pack_healthy=health.ready_to_render,
            )
            picked.append(
                DraftCandidate(
                    draft_id=did,
                    topic=draft.topic,
                    hook=draft.hook,
                    video_path=video,
                    duration_seconds=_probe_duration_safe(video),
                    score=score,
                    uploaded=is_up,
                    video_id=uploaded.get(did, ""),
                    pack_healthy=health.ready_to_render,
                    reasons=reasons,
                )
            )
        return picked

    return list_draft_candidates(limit=limit, require_video=True)
