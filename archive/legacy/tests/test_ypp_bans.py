from shorts_bot.compliance.upload_guard import check_upload_allowed
from shorts_bot.compliance.ypp_bans import (
    is_qa_iteration_title,
    metadata_bait_issues,
    title_compliance_issues,
)
from shorts_bot.config import settings
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.youtube.upload_guardrails import preflight_upload


def test_qa_iteration_title_blocked():
    assert is_qa_iteration_title("Motion alert (build v9 screen-only UI)")
    issues = title_compliance_issues("Your camera (build v2 fixed)")
    assert any("QA iteration" in i for i in issues)


def test_hashtag_title_blocked():
    issues = title_compliance_issues("DON'T LOOK #shorts #horror")
    assert any("hashtag" in i.lower() for i in issues)


def test_metadata_bait_blocked():
    issues = metadata_bait_issues("", "You won't believe this", "")
    assert issues


def test_upload_guard_blocks_qa_title(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ypp_safe_mode", True)
    store = MemoryStore(tmp_path / "y.db")
    mem = MemoryExtensions(store)
    script = (
        "You opened the security app at 3am and the hallway looked empty. "
        "You told yourself it was a glitch but the figure was closer when you refreshed. "
        "You checked the locks and heard a tap from the speaker. "
        "Something stood at the foot of your bed staring into the lens. "
        "It smiled then lunged at the camera while you watched alone."
    )
    report = check_upload_allowed(
        store,
        mem,
        draft_id=3,
        topic="security camera motion",
        hook="Your security camera flagged motion",
        script=script,
        title="Motion alert (build v16 best QC)",
        visibility="unlisted",
    )
    assert not report.allowed
    assert any("QA iteration" in i for i in report.issues)


def test_preflight_bans_allow_duplicate_draft(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ypp_safe_mode", True)
    store = MemoryStore(tmp_path / "p.db")
    mem = MemoryExtensions(store)
    pre = preflight_upload(
        store,
        mem,
        draft_id=1,
        topic="mirror",
        hook="You blinked",
        script="You blinked at the mirror and your reflection waited one second too long.",
        title="Mirror horror",
        allow_duplicate_draft=True,
    )
    assert not pre.allowed
    assert "allow_duplicate_draft" in pre.message
