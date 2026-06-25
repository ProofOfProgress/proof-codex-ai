"""Beat sheet gate — owner approval before Kling credits."""

from __future__ import annotations

from shorts_bot.production.video_beat_sheet import BeatEntry, beat_sheet_from_entries


def test_beat_sheet_from_entries():
    raw = [
        {"start_sec": 0, "end_sec": 5, "visual": "Fog road", "camera": "POV walk"},
    ]
    beats = beat_sheet_from_entries(raw)
    assert len(beats) == 1
    assert beats[0].visual == "Fog road"
