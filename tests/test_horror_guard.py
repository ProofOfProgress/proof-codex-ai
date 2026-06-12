from shorts_bot.production.horror_guard import ensure_horror_voice_before_pipeline


def test_auto_repair_first_person(tmp_path, monkeypatch):
    from shorts_bot.memory.store import MemoryStore
    from shorts_bot import config

    db = tmp_path / "db.sqlite"
    monkeypatch.setattr(config.settings, "database_path", db)
    monkeypatch.setattr(config.settings, "data_dir", tmp_path / "data")
    monkeypatch.setattr(config.settings, "pipeline_auto_horror_repair", True)

    store = MemoryStore(db)
    d = store.save_draft(
        "your security camera flagged motion — you live alone",
        "So, my security camera flagged motion. I live alone.",
        "My security camera flagged motion",
        "security cam scare",
    )
    store.review_draft(d.id, "approved", "ok")

    result = ensure_horror_voice_before_pipeline(
        store,
        d.id,
        hook=d.hook,
        script=d.script,
        help_angle=d.help_angle,
        topic=d.topic,
    )
    assert result.repaired
    assert "Your" in result.hook or "your" in result.hook.lower()
