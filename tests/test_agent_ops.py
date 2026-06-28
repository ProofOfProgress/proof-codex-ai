"""Tests for agent team mission log."""

from __future__ import annotations

import json

from shorts_bot.agent_ops.log import append_event, list_missions, mission_events, new_mission


def test_mission_lifecycle(tmp_path, monkeypatch):
    monkeypatch.setattr("shorts_bot.agent_ops.log.ops_dir", lambda: tmp_path)

    mid = new_mission("Test clip for car mount", owner="owner")
    assert len(mid) == 12

    append_event(mid, agent="ceo", event="dispatch_background", target="module1-qc-runner", message="QC while caption")
    append_event(mid, agent="product-video-prompt-builder", event="completed", message="Prompt ready")

    events = mission_events(mid)
    assert len(events) == 3
    assert events[0]["event"] == "mission_created"
    assert events[1]["target"] == "module1-qc-runner"
    assert events[-1]["agent"] == "product-video-prompt-builder"

    missions = list_missions()
    assert missions[0]["mission_id"] == mid
    assert "ceo" in missions[0]["agents"]


def test_mission_file_is_jsonl(tmp_path, monkeypatch):
    monkeypatch.setattr("shorts_bot.agent_ops.log.ops_dir", lambda: tmp_path)
    mid = new_mission("One event")
    path = tmp_path / f"{mid}.jsonl"
    assert path.exists()
    row = json.loads(path.read_text().strip().splitlines()[0])
    assert row["mission_id"] == mid


def test_ops_dir_creates_missions_folder(monkeypatch, tmp_path):
    import shorts_bot.agent_ops.log as log_mod

    target = tmp_path / "missions"
    monkeypatch.setattr(log_mod, "ops_dir", lambda: target.mkdir(parents=True, exist_ok=True) or target)
    assert log_mod.ops_dir() == target
    assert target.is_dir()
