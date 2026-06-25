def test_match_upload_by_video_id(tmp_path):
    from shorts_bot.compliance.upload_guard import record_upload
    from shorts_bot.memory.extensions import MemoryExtensions
    from shorts_bot.memory.store import MemoryStore
    from shorts_bot.learning.reflect import _match_upload

    db = tmp_path / "t.db"
    store = MemoryStore(db)
    mem = MemoryExtensions(store)
    record_upload(
        mem,
        draft_id=1,
        topic="morning reset",
        hook="hook",
        script="script",
        title="Morning reset tip",
        video_id="dQw4w9WgXcQ",
    )
    row = _match_upload(mem, "dQw4w9WgXcQ", metrics={"video_id": "dQw4w9WgXcQ"})
    assert row is not None
    assert row["video_id"] == "dQw4w9WgXcQ"
