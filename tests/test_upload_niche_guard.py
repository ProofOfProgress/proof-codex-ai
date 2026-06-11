from shorts_bot.compliance.upload_guard import check_upload_allowed
from shorts_bot.config import settings
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore


def test_blocks_off_niche_medieval_topic(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ypp_safe_mode", True)
    store = MemoryStore(tmp_path / "db.sqlite")
    mem = MemoryExtensions(store)
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
        draft_id=9,
        topic="Two friends medieval sword fight wholesome mock battle",
        hook="Epic medieval battles begin",
        script=script,
        title="Medieval Sword Fight",
    )
    assert not report.allowed
    assert any("off-niche" in i.lower() or "niche" in i.lower() for i in report.issues)
