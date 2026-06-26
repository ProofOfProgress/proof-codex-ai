"""Merge analytics sync rows with preserved manual/Studio fields."""

from __future__ import annotations

from typing import Any


def merge_metrics(existing: dict[str, Any] | None, incoming: dict[str, Any]) -> dict[str, Any]:
    """
    Key by video_id when present. Preserve manual swipe/retention across API syncs.
    Never invent swipe-away — unavailable stays unavailable until owner pastes real numbers.
    """
    base: dict[str, Any] = dict(existing or {})
    merged = dict(incoming)

    vid = str(merged.get("video_id") or base.get("video_id") or "").strip()
    if vid:
        merged["video_id"] = vid

    if vid:
        merged["video_label"] = vid
    elif base.get("video_label"):
        merged["video_label"] = base["video_label"]

    avg = merged.get("average_view_percentage")
    if avg is None and "retention_rate" in merged:
        avg = merged.get("retention_rate")
    if avg is not None and merged.get("retention_source") != "studio":
        merged["average_view_percentage"] = float(avg)
        merged.setdefault("retention_source", "analytics_api")

    old_swipe = base.get("viewed_vs_swiped_away") or base.get("swipe_away_inverse")
    old_swipe_src = str(base.get("swipe_source") or "")
    if old_swipe and old_swipe_src in ("studio", "manual", "tiktok"):
        merged["viewed_vs_swiped_away"] = old_swipe
        merged["swipe_source"] = old_swipe_src

    if base.get("retention_source") == "studio" and base.get("retention_rate"):
        merged["retention_rate"] = base["retention_rate"]
        merged["retention_source"] = "studio"

    if merged.get("swipe_source") != "unavailable" and not merged.get("viewed_vs_swiped_away"):
        merged["swipe_source"] = merged.get("swipe_source") or "unavailable"

    merged.setdefault("metrics_source", incoming.get("metrics_source") or "analytics_sync")
    if "metrics_window_days" in incoming:
        merged["metrics_window_days"] = incoming["metrics_window_days"]
    return merged
