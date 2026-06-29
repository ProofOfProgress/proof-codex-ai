"""Tests for daily click schedule."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from shorts_bot.desktop_hub.schedule import (
    DailyClickSchedule,
    load_schedule,
    save_schedule,
    should_run_now,
)


def test_should_run_at_scheduled_minute():
    sched = DailyClickSchedule(enabled=True, hour=14, minute=30, timezone="UTC", x=1, y=2)
    now = datetime(2026, 6, 29, 14, 30, 15, tzinfo=ZoneInfo("UTC"))
    assert should_run_now(sched, now=now)


def test_should_not_run_when_disabled():
    sched = DailyClickSchedule(enabled=False, hour=14, minute=30, timezone="UTC", x=1, y=2)
    now = datetime(2026, 6, 29, 14, 30, tzinfo=ZoneInfo("UTC"))
    assert not should_run_now(sched, now=now)


def test_save_and_load_schedule(tmp_path, monkeypatch):
    path = tmp_path / "schedule.json"
    monkeypatch.setattr("shorts_bot.desktop_hub.schedule.schedule_path", lambda: path)
    sched = DailyClickSchedule(
        enabled=True, hour=9, minute=0, timezone="America/Los_Angeles", x=100, y=200, label="test"
    )
    save_schedule(sched)
    loaded = load_schedule()
    assert loaded.x == 100 and loaded.enabled
