from shorts_bot.learning.reflect import reflect_after_production_review
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore


def test_reflect_after_production_review_records_phone_ui_lesson(tmp_path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "t.db"))
    msg = reflect_after_production_review(
        mem,
        draft_id=3,
        topic="security camera motion",
        score=65.0,
        production_score=50.0,
        fixes=["Align phone UI to screen rect"],
        phone_ui_issues=["Phone UI is a floating overlay"],
        visual_glitches=["Static UI during VO"],
    )
    assert msg is not None
    assert "production QC" in msg
    assert mem.get_training_config("avoid:phone-ui-overlay")


def test_reflect_skips_high_score_without_issues(tmp_path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "t.db"))
    msg = reflect_after_production_review(
        mem,
        draft_id=3,
        topic="test",
        score=92.0,
        production_score=90.0,
        fixes=[],
        phone_ui_issues=[],
        visual_glitches=[],
    )
    assert msg is None
