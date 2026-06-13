from shorts_bot.compliance.upload_guard import check_upload_allowed
from shorts_bot.config import settings
from shorts_bot.production.scare_pillar import scare_pillar_for_topic


def test_scare_pillar_classification():
    assert scare_pillar_for_topic("I remembered the Eye in my dream") == "dream_invasion"
    assert scare_pillar_for_topic("they worship the Eye in the barn") == "eye_worship"
    assert scare_pillar_for_topic("the villager smiled with wrong teeth") == "wrong_villager"
    assert scare_pillar_for_topic("the village sign showed my name") == "outsider_rule"


def test_upload_warns_same_pillar(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ypp_safe_mode", True)
    monkeypatch.setattr(settings, "database_path", tmp_path / "p.db")
    from shorts_bot.compliance.upload_guard import record_upload
    from shorts_bot.memory.extensions import MemoryExtensions
    from shorts_bot.memory.store import MemoryStore

    store = MemoryStore(tmp_path / "p.db")
    mem = MemoryExtensions(store)
    script = (
        "I dreamed the Eye filled the ceiling. I woke tasting metal. "
        "I told myself it was just a nightmare. The villager brought soup anyway. "
        "I remembered the Eye again when I blinked."
    )
    record_upload(
        mem,
        draft_id=2,
        topic="dream eye horror",
        hook="I remembered the Eye",
        script=script,
        title="Dream",
        video_id="v1",
    )
    report = check_upload_allowed(
        store,
        mem,
        draft_id=4,
        topic="I woke from another Eye dream",
        hook="I remembered the Eye again",
        script=script.replace("ceiling", "mirror"),
        title="Dream 2",
    )
    assert any("scare pillar" in i for i in report.issues)
