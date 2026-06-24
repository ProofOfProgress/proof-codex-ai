"""Retired horror + RTR lanes — stubs only."""

from __future__ import annotations

from shorts_bot.production.rtr_retired import rtr_lane_note


def horror_lane_for_qc() -> str:
    return f"AI / Tech Shorts (horror + {rtr_lane_note()})"


def horror_lane_compact() -> str:
    return horror_lane_for_qc()
