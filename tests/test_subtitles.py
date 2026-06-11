from shorts_bot.production.subtitles import build_subtitles_from_manifest


def test_build_srt_and_ass_offset_timeline():
    """Captions must start near 0 when timeline is normalized before render."""
    segments = [
        {"start_seconds": 0, "end_seconds": 5, "spoken_text": "I wake at 3am a lot."},
        {"start_seconds": 5, "end_seconds": 10, "spoken_text": "This helped me."},
    ]
    srt, _ = build_subtitles_from_manifest(segments, audio_duration=10.0)
    assert "00:00:00,000 -->" in srt


def test_build_srt_and_ass():
    segments = [
        {"start_seconds": 0, "end_seconds": 5, "spoken_text": "I wake at 3am a lot."},
        {"start_seconds": 5, "end_seconds": 10, "spoken_text": "This helped me."},
    ]
    srt, ass = build_subtitles_from_manifest(segments, audio_duration=10.0)
    assert "I wake at 3am" in srt
    assert "Dialogue:" in ass
    assert "00:00:00" in srt
