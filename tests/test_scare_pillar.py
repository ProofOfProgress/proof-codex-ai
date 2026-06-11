from shorts_bot.compliance.upload_guard import check_upload_allowed
from shorts_bot.config import settings
from shorts_bot.production.scare_pillar import scare_pillar_for_topic


def test_scare_pillar_classification():
    assert scare_pillar_for_topic("mirror reflection blinked") == "wrong_reflection"
    assert scare_pillar_for_topic("security camera flagged motion") == "wrong_place"
    assert scare_pillar_for_topic("knock from inside closet") == "wrong_sound"
    assert scare_pillar_for_topic("last text showed delivered") == "wrong_text"


def test_upload_warns_same_pillar(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ypp_safe_mode", True)
    monkeypatch.setattr(settings, "database_path", tmp_path / "p.db")
    from shorts_bot.compliance.upload_guard import record_upload
    from shorts_bot.memory.extensions import MemoryExtensions
    from shorts_bot.memory.store import MemoryStore

    store = MemoryStore(tmp_path / "p.db")
    mem = MemoryExtensions(store)
    script = (
        "You blinked at the mirror and your reflection blinked one second later. "
        "You blinked again staring at the glass. It did not blink. "
        "You turned away telling yourself it was just tired eyes and nothing moved. "
        "You heard a soft scrape from behind the door. You looked back. "
        "Your reflection was smiling but you were not. It raised a hand tapping the glass. "
        "It mouthed Mine. Then it lunged at you."
    )
    record_upload(
        mem,
        draft_id=2,
        topic="mirror blink horror",
        hook="You blinked",
        script=script,
        title="Mirror",
        video_id="v1",
    )
    report = check_upload_allowed(
        store,
        mem,
        draft_id=4,
        topic="the mirror showed wrong reflection",
        hook="Wrong reflection in mirror",
        script=script.replace("blinked later", "blinked again"),
        title="Mirror 2",
    )
    assert any("scare pillar" in w for w in report.warnings)
