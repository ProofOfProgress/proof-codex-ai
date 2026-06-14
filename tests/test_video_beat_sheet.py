"""Beat sheet gate — owner approval before Kling credits."""

from __future__ import annotations

from shorts_bot.config import settings
from shorts_bot.production.video_beat_sheet import (
    BeatEntry,
    beat_sheet_from_entries,
    default_beat_sheet_for_draft,
    ensure_beat_sheet,
    save_beat_sheet,
)


def test_beat_sheet_from_entries():
    raw = [
        {"start_sec": 0, "end_sec": 5, "visual": "Fog road", "camera": "POV walk"},
    ]
    beats = beat_sheet_from_entries(raw)
    assert len(beats) == 1
    assert beats[0].visual == "Fog road"


def test_default_beat_sheet_keeps_final_payoff():
    hook = "You saw a child point at the sky."
    script = (
        "You saw a child point at the sky. There was nothing there. "
        "You followed her gaze. The villagers kept walking. "
        "The road went quiet. The windows went black. "
        "A pressure opened above you. You looked up. "
        "It was him. He was watching you. He always watches."
    )

    beats = default_beat_sheet_for_draft(
        draft_id=1,
        topic="sky watcher",
        hook=hook,
        script=script,
    )

    visuals = [b.visual for b in beats]
    assert visuals[0] == hook
    assert visuals.count(hook) == 1
    assert "He always watches." in visuals[-1]


def test_default_beat_sheet_prefers_visual_beats():
    beats = default_beat_sheet_for_draft(
        draft_id=1,
        topic="sky watcher",
        hook="You saw a child point at the sky.",
        script="You looked up. He always watches.",
        visual_beats=[
            "A child points at a blank gray sky.",
            "A colossal unblinking eye fills the frame.",
            "Cut to black.",
        ],
    )

    assert [b.visual for b in beats[:3]] == [
        "A child points at a blank gray sky.",
        "A colossal unblinking eye fills the frame.",
        "Cut to black.",
    ]


def test_ensure_beat_sheet_regenerates_unapproved_missing_payoff(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    save_beat_sheet(
        7,
        [
            BeatEntry(0, 5, "You saw a child point at the sky."),
            BeatEntry(5, 10, "There was nothing there."),
            BeatEntry(10, 15, "Old superstitions, that's all."),
        ],
    )

    beats = ensure_beat_sheet(
        7,
        topic="sky watcher",
        hook="You saw a child point at the sky.",
        script=(
            "You saw a child point at the sky. There was nothing there. "
            "Old superstitions, that's all. He was watching you. He always watches."
        ),
    )

    assert "He always watches." in [b.visual for b in beats]
