from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.scare_pillar import scare_pillar_for_topic
from shorts_bot.production.topic_rotation import next_topic


def test_next_topic_skips_mirror_after_mirror_upload(tmp_path, monkeypatch):
    monkeypatch.setattr("shorts_bot.config.settings.database_path", tmp_path / "t.db")
    store = MemoryStore(tmp_path / "t.db")
    store.save_draft(
        topic="the mirror reflection blinked one second after you did",
        hook="mirror",
        script="You blinked at the mirror and your reflection blinked later. " * 4,
        help_angle="reflection",
    )
    d = store.list_drafts(limit=1)[0]
    store.review_draft(d.id, "approved", "test")

    from shorts_bot.compliance.upload_guard import record_upload
    from shorts_bot.memory.extensions import MemoryExtensions

    mem = MemoryExtensions(MemoryStore(tmp_path / "t.db"))
    record_upload(
        mem,
        draft_id=d.id,
        topic=d.topic,
        hook=d.hook,
        script=d.script,
        title="t",
        video_id="v1",
    )

    chosen = next_topic(store)
    assert scare_pillar_for_topic(chosen) != "wrong_reflection"
