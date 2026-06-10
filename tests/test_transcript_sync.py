from shorts_bot.production.transcript_sync import _words_to_timestamp_lines


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


def test_paid_stack_issues_assemblyai_key(monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.production.paid_stack import paid_stack_issues

    fake = Settings(
        require_paid_stack=True,
        allow_script_timing_fallback=False,
        resemble_api_key="x" * 20,
        resemble_voice_uuid="voice-uuid-12",
        transcript_provider="assemblyai",
        assemblyai_api_key=None,
    )
    monkeypatch.setattr("shorts_bot.production.paid_stack.settings", fake)
    issues = paid_stack_issues()
    assert any("AssemblyAI" in i for i in issues)
