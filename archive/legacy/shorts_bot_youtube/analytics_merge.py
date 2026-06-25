"""Merge API analytics with preserved Studio/manual fields — honest metrics only."""

from __future__ import annotations

from typing import Any


def merge_metrics(existing: dict[str, Any] | None, incoming: dict[str, Any]) -> dict[str, Any]:
    """
    Key by video_id when present. Preserve manual Studio fields across API syncs.
    Never invent swipe-away — API rows carry swipe_source=unavailable.
    """
    base: dict[str, Any] = dict(existing or {})
    merged = dict(incoming)

    vid = str(merged.get("video_id") or base.get("video_id") or "").strip()
    if vid:
        merged["video_id"] = vid

    # Prefer stable label: video_id > existing label > title slice
    if vid:
        merged["video_label"] = vid
    elif base.get("video_label"):
        merged["video_label"] = base["video_label"]

    # API average watch % is NOT Studio retention graph — store both names honestly
    avg = merged.get("average_view_percentage")
    if avg is None and "retention_rate" in merged:
        avg = merged.pop("retention_rate")
    if avg is not None:
        merged["average_view_percentage"] = float(avg)
        merged["retention_source"] = "youtube_analytics_api"

    # Preserve Studio/manual swipe across sync
    old_swipe = base.get("viewed_vs_swiped_away") or base.get("swipe_away_inverse")
    old_swipe_src = str(base.get("swipe_source") or "")
    if old_swipe and old_swipe_src in ("studio", "manual"):
        merged["viewed_vs_swiped_away"] = old_swipe
        merged["swipe_source"] = old_swipe_src

    # Preserve manual retention if explicitly from Studio
    if base.get("retention_source") == "studio" and base.get("retention_rate"):
        merged["retention_rate"] = base["retention_rate"]
        merged["retention_source"] = "studio"

    if merged.get("swipe_source") != "unavailable" and not merged.get("viewed_vs_swiped_away"):
        merged["swipe_source"] = merged.get("swipe_source") or "unavailable"

    merged["metrics_source"] = "youtube_analytics_api"
    if "metrics_window_days" in incoming:
        merged["metrics_window_days"] = incoming["metrics_window_days"]
    return merged


def find_existing_for_video(
    history: list[dict[str, Any]], video_id: str, title_label: str = ""
) -> dict[str, Any] | None:
    for row in history:
        m = row.get("metrics") or {}
        if video_id and str(m.get("video_id") or "") == video_id:
            return m
        if title_label and row.get("video_label") == title_label:
            return m
    return None
