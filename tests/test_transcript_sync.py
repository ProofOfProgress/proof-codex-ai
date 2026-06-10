from shorts_bot.production.transcript_sync import _normalize_gemini_transcript, _words_to_timestamp_lines


def test_words_to_timestamp_lines():
    words = [
        {"text": "hello", "start": 0},
        {"text": "world", "start": 1200},
        {"text": "again", "start": 5000},
    ]
    text = _words_to_timestamp_lines(words)
    assert "0:00 hello world" in text
    assert "0:05 again" in text


def test_paid_stack_accepts_assemblyai_source(monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.production.paid_stack import ensure_turboscribe_segments

    fake = Settings(allow_script_timing_fallback=False)
    monkeypatch.setattr("shorts_bot.production.paid_stack.settings", fake)
    ensure_turboscribe_segments("assemblyai")  # should not raise


def test_normalize_gemini_transcript():
    raw = "0:00 the minute before\n0:03 you breathe once\n[00:00:07] and stay"
    text = _normalize_gemini_transcript(raw)
    assert "0:00 the minute before" in text
    assert "0:03 you breathe once" in text


def test_paid_stack_issues_without_gemini(monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.production.paid_stack import paid_stack_issues

    fake = Settings(
        require_paid_stack=True,
        allow_script_timing_fallback=False,
        resemble_api_key="x" * 20,
        resemble_voice_uuid="voice-uuid-12",
        gemini_api_key=None,
        vision_qc_enabled=False,
        auto_upload_youtube=False,
    )
    monkeypatch.setattr("shorts_bot.production.paid_stack.settings", fake)
    issues = paid_stack_issues()
    assert any("GEMINI" in i for i in issues)


def test_paid_stack_accepts_gemini_source(monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.production.paid_stack import ensure_turboscribe_segments

    fake = Settings(allow_script_timing_fallback=False)
    monkeypatch.setattr("shorts_bot.production.paid_stack.settings", fake)
    ensure_turboscribe_segments("gemini")
