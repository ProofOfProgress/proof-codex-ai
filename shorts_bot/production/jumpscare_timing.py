"""Russian-roulette jumpscare timing — vary scare beat per Short (not always final 3s)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

JumpscareProfile = Literal[
    "finale",  # classic: last segment + late sting
    "early_snap",  # scare ~35–45% in — viewers think they're safe
    "late_hold",  # sting hugs the very end after long false calm
    "mid_twist",  # scare ~50–60% then dread coda
    "double_tap",  # fake scare mid + real lunge finale
]

_PROFILES: tuple[JumpscareProfile, ...] = (
    "finale",
    "early_snap",
    "late_hold",
    "mid_twist",
    "double_tap",
)


@dataclass(frozen=True)
class JumpscarePlan:
    profile: JumpscareProfile
    primary_segment_index: int
    decoy_segment_index: int | None
    sting_start_ratio: float  # fallback when segment times unknown (0–1 of total duration)
    volume_warning: str
    creator_note: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> JumpscarePlan:
        return cls(
            profile=data.get("profile", "finale"),
            primary_segment_index=int(data.get("primary_segment_index", 0)),
            decoy_segment_index=data.get("decoy_segment_index"),
            sting_start_ratio=float(data.get("sting_start_ratio", 0.88)),
            volume_warning=str(data.get("volume_warning", "")),
            creator_note=str(data.get("creator_note", "")),
        )


def _segment_index(segment_count: int, ratio: float, *, min_index: int = 1) -> int:
    if segment_count <= 1:
        return 0
    idx = int(round(ratio * (segment_count - 1)))
    return min(max(idx, min_index), segment_count - 1)


def plan_for_draft(draft_id: int, segment_count: int) -> JumpscarePlan:
    """Deterministic per draft_id — rotates profiles across the upload calendar."""
    n = max(1, draft_id)
    profile = _PROFILES[n % len(_PROFILES)]
    last = max(0, segment_count - 1)

    if profile == "finale":
        return JumpscarePlan(
            profile=profile,
            primary_segment_index=last,
            decoy_segment_index=None,
            sting_start_ratio=0.86,
            volume_warning="🔊 VOLUME WARNING — jumpscare hits near the end. Headphones advised.",
            creator_note="Finale scare — classic last-beat lunge.",
        )
    if profile == "early_snap":
        primary = _segment_index(segment_count, 0.40, min_index=1)
        return JumpscarePlan(
            profile=profile,
            primary_segment_index=primary,
            decoy_segment_index=None,
            sting_start_ratio=min(0.55, (primary + 1) / max(segment_count, 1)),
            volume_warning="🔊 VOLUME WARNING — scare may hit EARLY. Headphones advised.",
            creator_note="Early snap — Russian roulette; scare before the 'safe' ending.",
        )
    if profile == "late_hold":
        return JumpscarePlan(
            profile=profile,
            primary_segment_index=last,
            decoy_segment_index=None,
            sting_start_ratio=0.94,
            volume_warning="🔊 VOLUME WARNING — jumpscare hits at the LAST second. Headphones advised.",
            creator_note="Late hold — maximum delay after false calm.",
        )
    if profile == "mid_twist":
        primary = _segment_index(segment_count, 0.55, min_index=1)
        return JumpscarePlan(
            profile=profile,
            primary_segment_index=primary,
            decoy_segment_index=None,
            sting_start_ratio=min(0.72, (primary + 1) / max(segment_count, 1)),
            volume_warning="🔊 VOLUME WARNING — jumpscare timing UNPREDICTABLE. Headphones advised.",
            creator_note="Mid twist — scare in the middle, dread lingers after.",
        )
    # double_tap
    decoy = _segment_index(segment_count, 0.42, min_index=1)
    return JumpscarePlan(
        profile=profile,
        primary_segment_index=last,
        decoy_segment_index=decoy if decoy < last else None,
        sting_start_ratio=0.88,
        volume_warning="🔊 VOLUME WARNING — DOUBLE scare (fake then real). Headphones advised.",
        creator_note="Double tap — decoy motion mid, real lunge at finale.",
    )


def sting_start_seconds(
    plan: JumpscarePlan,
    *,
    segments: list[dict],
    total_duration: float,
) -> float:
    """When to start the audio sting based on plan + manifest segment times."""
    if total_duration <= 0:
        return 0.0
    if segments and 0 <= plan.primary_segment_index < len(segments):
        seg = segments[plan.primary_segment_index]
        end = float(seg.get("end_seconds") or 0)
        start = float(seg.get("start_seconds") or 0)
        if end > start:
            # Sting leads into the primary scare segment's last ~40%
            span = end - start
            return max(0.0, min(total_duration - 0.5, start + span * 0.55))
    return max(0.0, min(total_duration - 0.5, total_duration * plan.sting_start_ratio))


def scare_sentence_indices(plan: JumpscarePlan, sentence_count: int) -> set[int]:
    """TTS prosody — which sentences get jumpscare delivery (not always the last)."""
    if sentence_count <= 0:
        return set()
    last = sentence_count - 1
    if plan.profile == "finale" or plan.profile == "late_hold":
        return {last}
    if plan.profile == "early_snap":
        return {max(0, int(sentence_count * 0.42))}
    if plan.profile == "mid_twist":
        return {max(0, int(sentence_count * 0.52))}
    # double_tap
    decoy = max(0, int(sentence_count * 0.40))
    return {decoy, last}


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
