from pathlib import Path
from unittest.mock import patch

from shorts_bot.production.image_prompts import ai_segment_to_prompt
from shorts_bot.production.turboscribe_parser import TranscriptSegment


def test_ai_segment_prompt_has_no_text_rule():
    seg = TranscriptSegment(start_seconds=7.0, text="I wake at 3am", label="00.07")
    prompt = ai_segment_to_prompt(seg, topic="sleep")
    assert "no text" in prompt.lower()
    assert "9:16" in prompt or "vertical" in prompt.lower()
    assert "3am" in prompt.lower() or "wake" in prompt.lower()


def test_render_ai_frame_writes_caption(tmp_path: Path, monkeypatch):
    from shorts_bot.production.render_ai_images import render_ai_frame
    from shorts_bot.production.image_prompts import ImageBrief

    brief = ImageBrief(
        start_seconds=0,
        end_seconds=5,
        filename_stem="00.00",
        spoken_text="Try this tonight.",
        prompt="calm room still",
    )
    out = tmp_path / "00.00.png"

    def fake_generate(prompt, path):
        from PIL import Image

        Image.new("RGB", (1080, 1920), "#0B1020").save(path, "PNG")
        return "replicate/test"

    monkeypatch.setattr(
        "shorts_bot.production.render_ai_images.generate_image",
        fake_generate,
    )
    assert render_ai_frame(brief, out) is True
    assert out.exists()
    assert out.stat().st_size > 100


def test_pack_ai_fallback_without_api_key(tmp_path: Path, monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.memory.store import MemoryStore
    from shorts_bot.production.pack import auto_produce_draft

    fake = Settings(
        data_dir=tmp_path,
        database_path=tmp_path / "t.db",
        visual_style="ai",
        video_backend="legacy_i2v",
        replicate_api_token=None,
        fal_api_key=None,
        require_paid_stack=False,
        allow_script_timing_fallback=True,
    )
    monkeypatch.setattr("shorts_bot.config.settings", fake)
    monkeypatch.setattr("shorts_bot.production.pack.settings", fake)
    monkeypatch.setattr("shorts_bot.production.paid_stack.settings", fake)

    store = MemoryStore(tmp_path / "t.db")
    d = store.save_draft(
        topic="sleep",
        script="You wake at 3 a.m. Your phone stays dark. One breath.",
        hook="Before your phone",
        help_angle="helps",
        quality_notes="ok",
    )
    import pytest

    with pytest.raises(RuntimeError, match="paid image stack"):
        auto_produce_draft(store, d.id, render_images=True)
