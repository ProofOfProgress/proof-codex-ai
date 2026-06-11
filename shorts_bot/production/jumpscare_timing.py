"""Jumpscare timing — finale scare near the end, or suspense-into-replay (no scare)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

JumpscareProfile = Literal[
    "finale",  # classic: lunge on last beat, sting ~2s before video end
    "suspense_replay",  # no jumpscare — dread hold, Shorts replay bait
]


@dataclass(frozen=True)
class JumpscarePlan:
    profile: JumpscareProfile
    primary_segment_index: int
    decoy_segment_index: int | None
    has_jumpscare: bool
    sting_start_ratio: float  # fallback when segment times unknown (0–1 of total duration)
    volume_warning: str
    creator_note: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> JumpscarePlan:
        profile = data.get("profile", "finale")
        has_js = data.get("has_jumpscare")
        if has_js is None:
            has_js = profile != "suspense_replay"
        return cls(
            profile=profile,
            primary_segment_index=int(data.get("primary_segment_index", 0)),
            decoy_segment_index=data.get("decoy_segment_index"),
            has_jumpscare=bool(has_js),
            sting_start_ratio=float(data.get("sting_start_ratio", 0.88)),
            volume_warning=str(data.get("volume_warning", "")),
            creator_note=str(data.get("creator_note", "")),
        )


def plan_for_draft(draft_id: int, segment_count: int) -> JumpscarePlan:
    """
    Deterministic per draft_id.

    ~2/3 finale jumpscare (last beat, sting a couple seconds before end).
    ~1/3 suspense_replay (no scare — tension holds into Shorts auto-replay).
    """
    last = max(0, segment_count - 1)
    if draft_id % 3 == 0:
        return JumpscarePlan(
            profile="suspense_replay",
            primary_segment_index=last,
            decoy_segment_index=None,
            has_jumpscare=False,
            sting_start_ratio=0.0,
            volume_warning="",
            creator_note="Suspense hold — no jumpscare; dread into replay.",
        )
    return JumpscarePlan(
        profile="finale",
        primary_segment_index=last,
        decoy_segment_index=None,
        has_jumpscare=True,
        sting_start_ratio=0.92,
        volume_warning="🔊 VOLUME WARNING — jumpscare at the end. Use headphones.",
        creator_note="Finale scare — lunge on last beat, sting ~2s before end.",
    )


def sting_start_seconds(
    plan: JumpscarePlan,
    *,
    segments: list[dict],
    total_duration: float,
) -> float | None:
    """
    When to start the audio sting — aligned to the finale visual flash, not wall-clock end.

    Render applies zoom/brightness only in the last ~0.28s of the primary scare segment clip.
    """
    if not plan.has_jumpscare or total_duration <= 1.0:
        return None

    from shorts_bot.config import settings

    flash_lead = 0.28  # matches _jumpscare_video_filter in render_video.py
    idx = plan.primary_segment_index
    if segments and 0 <= idx < len(segments):
        seg = segments[idx]
        seg_start = float(seg.get("start_seconds", 0))
        seg_end = float(seg.get("end_seconds", seg_start))
        seg_dur = max(0.35, seg_end - seg_start)
        visual_flash_at = seg_start + max(0.0, seg_dur - flash_lead)
        # Sting just before the visible pop (not ~2.5s before video end).
        return max(0.0, visual_flash_at - 0.06)

    lead = min(max(1.5, settings.jumpscare_sting_seconds), total_duration * 0.12)
    lead = min(lead, 3.0)
    return max(0.0, total_duration - lead)


def scare_sentence_indices(plan: JumpscarePlan, sentence_count: int) -> set[int]:
    """TTS prosody — jumpscare delivery only on finale last sentence."""
    if sentence_count <= 0 or not plan.has_jumpscare:
        return set()
    return {sentence_count - 1}


def load_plan_for_draft(draft_id: int, segment_count: int) -> JumpscarePlan:
    from shorts_bot.drafts.meta import load_draft_meta

    meta = load_draft_meta(draft_id)
    raw = meta.get("jumpscare_plan")
    if isinstance(raw, dict) and raw.get("profile"):
        plan = JumpscarePlan.from_dict(raw)
        if segment_count > 0 and plan.primary_segment_index >= segment_count:
            return plan_for_draft(draft_id, segment_count)
        return plan
    return plan_for_draft(draft_id, segment_count)


def persist_plan(draft_id: int, plan: JumpscarePlan) -> None:
    from shorts_bot.drafts.meta import save_draft_meta

    save_draft_meta(draft_id, jumpscare_plan=plan.to_dict())
