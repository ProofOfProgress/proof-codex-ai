from shorts_bot.production.queue_cli import _production_status, next_draft_id


def test_next_draft_prefers_incomplete(tmp_path, monkeypatch):
    from shorts_bot.memory.store import MemoryStore
    import shorts_bot.production.queue_cli as qc

    prod = tmp_path / "production"
    monkeypatch.setattr(qc, "_pack_dir", lambda draft_id: prod / f"draft_{draft_id}")

    store = MemoryStore(tmp_path / "test.db")
    d1 = store.save_draft("topic a", "script a", "hook a", "angle a")
    d2 = store.save_draft("topic b", "script b", "hook b", "angle b")
    store.review_draft(d1.id, "approved", "ok")
    store.review_draft(d2.id, "approved", "ok")

    pack1 = prod / f"draft_{d1.id}"
    pack1.mkdir(parents=True, exist_ok=True)
    (pack1 / "final_short.mp4").write_bytes(b"\x00" * 60_000)

    assert next_draft_id(store) == d2.id


def test_production_status_empty_pack():
    st = _production_status(9999)
    assert st["clips"] == 0
    assert not st["has_final"]
