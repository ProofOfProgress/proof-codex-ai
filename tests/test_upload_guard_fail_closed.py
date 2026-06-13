def test_duplicate_title_check_fails_closed(tmp_path, monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.memory.extensions import MemoryExtensions
    from shorts_bot.memory.store import MemoryStore
    from shorts_bot.youtube.upload_guardrails import preflight_upload

    db = tmp_path / "t.db"
    store = MemoryStore(db)
    mem = MemoryExtensions(store)
    d = store.save_draft(
        topic="topic",
        script="script text here",
        hook="hook",
        help_angle="helps",
    )

    def boom(*_a, **_k):
        raise RuntimeError("YouTube API down")

    monkeypatch.setattr(
        "shorts_bot.youtube.channel_videos.list_channel_videos",
        boom,
    )
    monkeypatch.setattr("shorts_bot.youtube.google_auth.credentials_configured", lambda: True)
    monkeypatch.setattr("shorts_bot.youtube.google_auth.token_exists", lambda: True)
    fake = Settings(
        database_path=db,
        block_duplicate_title_upload=True,
        block_duplicate_draft_upload=False,
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
        title="Unique title for test",
    )
    assert not pre.allowed
    assert "Duplicate-title check failed" in pre.message
