from pathlib import Path

from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.pack import auto_produce_draft
from shorts_bot.production.script_segments import segments_from_script


def test_segments_from_script():
    segs = segments_from_script("Line one. Line two here. And line three.")
    assert len(segs) >= 3
    assert segs[1].start_seconds > segs[0].start_seconds


def test_auto_produce_renders_images(tmp_path: Path, monkeypatch):
    from shorts_bot.config import Settings

    fake = Settings(
        data_dir=tmp_path,
        require_paid_stack=False,
        allow_script_timing_fallback=True,
        visual_style="hybrid",
        replicate_api_token="r8_test_token_for_pytest",
        ai_video_generation_enabled=False,
    )
    monkeypatch.setattr("shorts_bot.config.settings", fake)
    monkeypatch.setattr("shorts_bot.production.pack.settings", fake)
    monkeypatch.setattr("shorts_bot.production.paid_stack.settings", fake)

    def _fake_render(briefs, images_dir):
        images_dir.mkdir(parents=True, exist_ok=True)
        for b in briefs:
            (images_dir / f"{b.filename_stem}.png").write_bytes(b"png")
        return len(briefs)

    monkeypatch.setattr("shorts_bot.production.pack.render_all_ai_images", _fake_render)

    store = MemoryStore(tmp_path / "t.db")
    d = store.save_draft(
        topic="sleep",
        script="You wake at 3 a.m. Your phone stays dark. One breath. You're still here.",
        hook="Stop scrolling.",
        help_angle="helps",
        quality_notes="ok",
    )
    pack = auto_produce_draft(
        store,
        d.id,
        render_images=True,
    )
    assert pack.images_rendered >= 1
    assert (pack.output_dir / "images").exists()
    assert (pack.output_dir / "VOICEOVER_SCRIPT.txt").exists()
