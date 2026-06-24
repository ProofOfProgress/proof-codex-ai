"""Rapid Tool Review lane — retired 2026-06-24 (same as Peripheral horror)."""

from __future__ import annotations

ARCHIVE_ROOT = "archive/rapid_tool_review"
RETIRED_LABEL = "Rapid Tool Review"


class RapidToolReviewRetired(RuntimeError):
    """Raised when production code paths assume active RTR branding."""

    def __init__(self, detail: str = "") -> None:
        msg = (
            f"{RETIRED_LABEL} is retired (2026-06-24). "
            f"Archived under {ARCHIVE_ROOT}/ — do not use for new uploads. "
            "Owner must lock the next niche/brand."
        )
        if detail:
            msg = f"{msg} ({detail})"
        super().__init__(msg)


def rtr_lane_note() -> str:
    return f"{RETIRED_LABEL} retired — see {ARCHIVE_ROOT}/ (reference only)."
