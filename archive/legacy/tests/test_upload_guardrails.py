def test_preflight_blocks_duplicate_draft(tmp_path, monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.memory.extensions import MemoryExtensions
    from shorts_bot.memory.store import MemoryStore
    from shorts_bot.compliance.upload_guard import record_upload
    from shorts_bot.youtube.upload_guardrails import preflight_upload

    db = tmp_path / "t.db"
    store = MemoryStore(db)
    mem = MemoryExtensions(store)
    d = store.save_draft(
        topic="office bathroom",
        script="I hide in the stall and breathe.",
        hook="The minute I hide",
        help_angle="helps",
    )
    record_upload(
        mem,
        draft_id=d.id,
        topic=d.topic,
        hook=d.hook,
        script=d.script,
        title="Office bathroom reset",
        video_id="abc123xyz01",
    )

    fake = Settings(
        database_path=db,
        block_duplicate_draft_upload=True,
        ypp_safe_mode=False,
    )
    monkeypatch.setattr("shorts_bot.youtube.upload_guardrails.settings", fake)

    pre = preflight_upload(
        store,
        mem,
        draft_id=d.id,
        topic=d.topic,
        hook=d.hook,
        script=d.script,
        title="Office bathroom reset v2",
    )
    assert not pre.allowed
    assert "abc123xyz01" in pre.message
