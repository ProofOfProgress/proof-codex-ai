from datetime import datetime, timedelta, timezone

from shorts_bot.compliance.upload_guard import check_upload_allowed, record_upload
from shorts_bot.config import settings
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore


def test_voided_upload_ignored_by_guard(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ypp_safe_mode", True)
    monkeypatch.setattr(settings, "max_uploads_per_24h", 1)
    store = MemoryStore(tmp_path / "db.sqlite")
    mem = MemoryExtensions(store)

    record_upload(
        mem,
        draft_id=1,
        topic="medieval swords",
        hook="wrong",
        script="wrong script",
        title="Wrong",
        video_id="JIkMhPH0l6o",
    )
    mem.void_upload_events(video_id="JIkMhPH0l6o")
    assert mem.recent_uploads(hours=24) == []

    script = (
        "You blinked at the mirror and your reflection blinked one second later. "
        "You stepped closer and the glass stayed still, but the eyes in it didn't. "
        "You raised your phone to record proof and the screen showed an empty bathroom. "
        "You looked up — the reflection was already facing the door behind you. "
        "You told yourself it was a lag. You turned to leave. It lunged."
    )
    report = check_upload_allowed(
        store,
        mem,
        draft_id=3,
        topic="security cam motion",
        hook="Your security camera flagged motion at 3:12 AM — you live alone",
        script=script,
        title="🔊 Motion alert at 3:12 AM — you live alone",
    )
    assert report.allowed
