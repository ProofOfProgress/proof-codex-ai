from datetime import datetime, timedelta, timezone
from pathlib import Path

from shorts_bot.compliance.inauthentic_rules import risk_signals_for_script
from shorts_bot.compliance.upload_guard import check_upload_allowed, record_upload
from shorts_bot.config import settings
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore


def _mem(tmp_path: Path) -> tuple[MemoryStore, MemoryExtensions]:
    store = MemoryStore(tmp_path / "ypp.db")
    return store, MemoryExtensions(store)


_GOOD_SCRIPT = (
    "I used to wake at 3am every night. My brain would lap the same worry. "
    "Honestly for me the fix was simple — phone stays dark, one breath, name the thought, "
    "three slow breaths. You're still here. Good."
)


def test_risk_flags_spam_phrase():
    risks = risk_signals_for_script(
        "In today's fast-paced world you need better sleep habits every night.",
        "Sleep tips",
        "Before sleep — one thing",
    )
    assert any("spam-farm" in r for r in risks)
    assert any("first-person" in r for r in risks)


def test_upload_allowed_good_script(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "ypp_safe_mode", True)
    store, mem = _mem(tmp_path)
    report = check_upload_allowed(
        store,
        mem,
        draft_id=1,
        topic="sleep at 3am",
        hook="I wake at 3am and my brain won't stop",
        script=_GOOD_SCRIPT,
        title="Before 3am spirals — what helped me #Shorts",
    )
    assert report.allowed
    assert not report.issues


def test_upload_blocked_no_first_person(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "ypp_safe_mode", True)
    store, mem = _mem(tmp_path)
    report = check_upload_allowed(
        store,
        mem,
        draft_id=2,
        topic="focus",
        hook="Focus better",
        script="Focus is important for students. Here are five tips for productivity.",
        title="Focus tips #Shorts",
    )
    assert not report.allowed
    assert any("first-person" in i for i in report.issues)


def test_upload_blocked_rate_limit(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "ypp_safe_mode", True)
    monkeypatch.setattr(settings, "max_uploads_per_24h", 1)
    store, mem = _mem(tmp_path)
    record_upload(
        mem,
        draft_id=1,
        topic="sleep",
        hook="hook one",
        script=_GOOD_SCRIPT,
        title="Title one",
        video_id="vid1",
    )
    report = check_upload_allowed(
        store,
        mem,
        draft_id=2,
        topic="boundaries",
        hook="I need boundaries before the text",
        script=_GOOD_SCRIPT.replace("3am", "the text"),
        title="Before the text — what I do #Shorts",
    )
    assert not report.allowed
    assert any("24h" in i for i in report.issues)


def test_upload_blocked_topic_cooldown(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "ypp_safe_mode", True)
    monkeypatch.setattr(settings, "max_uploads_per_24h", 5)
    store, mem = _mem(tmp_path)
    with mem._conn() as conn:
        old = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        conn.execute(
            """
            INSERT INTO upload_events (draft_id, topic, hook, script, title, video_id, uploaded_at)
            VALUES (1, 'sleep at 3am', 'old hook', ?, 'old title', 'v0', ?)
            """,
            (_GOOD_SCRIPT, old),
        )
    report = check_upload_allowed(
        store,
        mem,
        draft_id=3,
        topic="sleep at 3am",
        hook="Different hook for sleep",
        script=_GOOD_SCRIPT,
        title="Sleep help #Shorts",
    )
    assert not report.allowed
    assert any("topic" in i.lower() for i in report.issues)


def test_ypp_safe_mode_off_skips_guard(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "ypp_safe_mode", False)
    store, mem = _mem(tmp_path)
    report = check_upload_allowed(
        store,
        mem,
        draft_id=9,
        topic="x",
        hook="y",
        script="Generic lecture with no personal voice.",
        title="CLICK BAIT TITLE WOW",
    )
    assert report.allowed
