def test_finish_video_ok_false_on_qc_fail(monkeypatch, tmp_path):
    from shorts_bot.config import Settings
    from shorts_bot.memory.store import MemoryStore
    from shorts_bot.production.pipeline import PipelineResult
    from shorts_bot.services.ops import BotOperations

    db = tmp_path / "t.db"
    store = MemoryStore(db)
    draft = store.save_draft(
        topic="test qc",
        script="I breathe slowly when the room gets loud.",
        hook="The minute it gets loud",
        help_angle="helps",
    )

    fake_result = PipelineResult(
        draft_id=draft.id,
        pack_dir=tmp_path / "pack",
        messages=["Video QC failed: too short"],
        video_path=tmp_path / "pack" / "final_short.mp4",
        upload_url=None,
        success=False,
        qc_passed=False,
    )

    def fake_pipeline(_store, draft_id, **kwargs):
        return fake_result

    fake_settings = Settings(database_path=db, data_dir=tmp_path)
    monkeypatch.setattr("shorts_bot.config.settings", fake_settings)
    monkeypatch.setattr("shorts_bot.services.ops.settings", fake_settings)
    monkeypatch.setattr("shorts_bot.services.ops.get_store", lambda: store)
    monkeypatch.setattr(
        "shorts_bot.production.pipeline.finish_draft_pipeline",
        fake_pipeline,
    )

    out = BotOperations().finish_video(draft.id, upload=False)
    assert out["ok"] is False
    assert out["qc_passed"] is False
