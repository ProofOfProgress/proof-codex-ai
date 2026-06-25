from pathlib import Path

from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.pack import build_production_pack
from shorts_bot.production.script_segments import segments_from_script


def test_segments_from_script():
    segs = segments_from_script("Line one. Line two here. And line three.")
    assert len(segs) >= 3
    assert segs[1].start_seconds > segs[0].start_seconds


def test_build_production_pack_invideo(tmp_path: Path, monkeypatch):
    from shorts_bot.config import Settings

    fake = Settings(data_dir=tmp_path)
    monkeypatch.setattr("shorts_bot.config.settings", fake)
    monkeypatch.setattr("shorts_bot.invideo.script_pack.settings", fake)

    store = MemoryStore(tmp_path / "t.db")
    d = store.save_draft(
        topic="ChatGPT Plus",
        script="Pay or skip?",
        hook="Everyone pays for ChatGPT Plus.",
        help_angle="review",
        quality_notes="ok",
    )
    pack = build_production_pack(store, draft_id=d.id)
    assert pack.draft_id == d.id
    assert (pack.output_dir / "script.txt").is_file()
    assert pack.manifest_path.is_file()
