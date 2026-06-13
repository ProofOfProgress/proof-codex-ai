import pytest

from shorts_bot.production.paid_stack import (
    ensure_resemble_voice,
    ensure_turboscribe_segments,
    paid_stack_issues,
)


def test_paid_stack_issues_when_resemble_missing(monkeypatch):
    from shorts_bot.config import Settings

    fake = Settings(
        require_paid_stack=True,
        allow_free_tts_fallback=False,
        video_backend="legacy_i2v",
        resemble_api_key=None,
        resemble_voice_uuid=None,
        gemini_api_key="a" * 24,
        vision_qc_enabled=False,
        auto_upload_youtube=False,
    )
    monkeypatch.setattr("shorts_bot.production.paid_stack.settings", fake)
    issues = paid_stack_issues()
    assert any("Resemble" in i for i in issues)


def test_paid_stack_skips_resemble_when_kling_native_audio(monkeypatch):
    from shorts_bot.config import Settings

    fake = Settings(
        require_paid_stack=True,
        allow_free_tts_fallback=False,
        video_backend="kling",
        kling_generate_audio=True,
        kling_skip_narrator_tts=True,
        resemble_api_key=None,
        resemble_voice_uuid=None,
        gemini_api_key="a" * 24,
        vision_qc_enabled=False,
        auto_upload_youtube=False,
    )
    monkeypatch.setattr("shorts_bot.production.paid_stack.settings", fake)
    issues = paid_stack_issues()
    assert not any("Resemble" in i for i in issues)


def test_ensure_turboscribe_blocks_script_fallback(monkeypatch):
    from shorts_bot.config import Settings

    fake = Settings(allow_script_timing_fallback=False)
    monkeypatch.setattr("shorts_bot.production.paid_stack.settings", fake)
    with pytest.raises(RuntimeError, match="transcript timestamps"):
        ensure_turboscribe_segments("script_duration")


def test_ensure_resemble_blocks_without_keys(monkeypatch):
    from shorts_bot.config import Settings

    fake = Settings(
        require_paid_stack=True,
        tts_provider="resemble",
        allow_free_tts_fallback=False,
        video_backend="legacy_i2v",
        resemble_api_key=None,
        resemble_voice_uuid=None,
    )
    monkeypatch.setattr("shorts_bot.production.paid_stack.settings", fake)
    with pytest.raises(RuntimeError, match="Resemble"):
        ensure_resemble_voice()


def test_ensure_turboscribe_skipped_for_kling_native(monkeypatch):
    from shorts_bot.config import Settings

    fake = Settings(
        allow_script_timing_fallback=False,
        video_backend="kling",
        kling_generate_audio=True,
        kling_skip_narrator_tts=True,
    )
    monkeypatch.setattr("shorts_bot.production.paid_stack.settings", fake)
    ensure_turboscribe_segments("script_estimate")
    from shorts_bot.config import Settings

    fake = Settings(
        require_paid_stack=True,
        tts_provider="resemble",
        allow_free_tts_fallback=False,
        video_backend="kling",
        kling_generate_audio=True,
        kling_skip_narrator_tts=True,
        resemble_api_key=None,
        resemble_voice_uuid=None,
    )
    monkeypatch.setattr("shorts_bot.production.paid_stack.settings", fake)
    ensure_resemble_voice()
