"""Per-draft production variety — anti-fingerprint rotation (2026 YPP / classifier research)."""

from __future__ import annotations

from dataclasses import dataclass

from shorts_bot.config import settings


@dataclass(frozen=True)
class VarietyProfile:
    """Deterministic variety axes keyed by draft_id — varies each Short."""

    draft_id: int
    zoom_motion: str  # in | out | none
    caption_y_offset: int  # px from default anchor
    figure_x_offset: int  # px from default anchor
    segment_merge_bias: float  # 0.85–1.15 scales visual cut length
    hook_pacing: str  # calm | normal | brisk

    def summary(self) -> str:
        return (
            f"variety d{self.draft_id}: zoom={self.zoom_motion}, "
            f"captionΔy={self.caption_y_offset}, figureΔx={self.figure_x_offset}, "
            f"cuts×{self.segment_merge_bias:.2f}, pace={self.hook_pacing}"
        )


def variety_for_draft(draft_id: int) -> VarietyProfile:
    """Rotate axes without randomness — reproducible per draft."""
    if not settings.production_variety_enabled:
        return VarietyProfile(
            draft_id=draft_id,
            zoom_motion="none",
            caption_y_offset=0,
            figure_x_offset=0,
            segment_merge_bias=1.0,
            hook_pacing="normal",
        )

    n = max(1, draft_id)
    zoom_opts = ("in", "out", "none", "in", "out")
    pace_opts = ("calm", "normal", "brisk", "normal", "calm")
    return VarietyProfile(
        draft_id=draft_id,
        zoom_motion=zoom_opts[n % len(zoom_opts)],
        caption_y_offset=((n * 17) % 5 - 2) * 12,  # -24..+24
        figure_x_offset=((n * 11) % 5 - 2) * 18,  # -36..+36
        segment_merge_bias=0.88 + (n % 5) * 0.06,  # 0.88–1.12
        hook_pacing=pace_opts[n % len(pace_opts)],
    )
