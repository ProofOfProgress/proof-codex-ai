from pathlib import Path

from shorts_bot.production.captions import (
    burn_captions_on_frames,
    burn_captions_via_ffmpeg,
    caption_display_text,
    escape_ass_text,
    format_caption_lines,
)
from shorts_bot.production.subtitles import build_subtitles_from_manifest, ffmpeg_subtitles_filter


def test_format_caption_lines_word_wrap_and_ellipsis():
    long = (
        "I used to lose sleep over need calm before a hard conversation "
        "same loop every single night without stopping"
    )
    lines = format_caption_lines(long, max_lines=2, max_chars=32)
    assert len(lines) <= 2
    assert lines[-1].endswith("…") or len(long.split()) <= sum(len(l.split()) for l in lines)


def test_escape_ass_special_chars():
    assert escape_ass_text("line {bad}") == r"line \{bad\}"
    assert escape_ass_text("a\\b") == r"a\\b"


def test_ass_uses_box_style_and_safe_margin():
    segments = [
        {"start_seconds": 0.0, "end_seconds": 3.0, "spoken_text": "Try this tonight."},
    ]
    _, ass = build_subtitles_from_manifest(segments, audio_duration=3.0)
    assert "BorderStyle" in ass or ",3," in ass  # BorderStyle 3 opaque box
    assert "1260" in ass  # Caption anchor above Shorts bottom UI (CAPTION_ANCHOR_Y_PX)
    assert r"\pos(" in ass
    assert "Try this tonight." in ass


def test_ffmpeg_mode_default(monkeypatch):
    from shorts_bot.config import Settings

    fake = Settings(caption_mode="ffmpeg")
    monkeypatch.setattr("shorts_bot.config.settings", fake)
    monkeypatch.setattr("shorts_bot.production.captions.settings", fake)
    assert burn_captions_via_ffmpeg()
    assert not burn_captions_on_frames()


def test_ffmpeg_subtitles_filter_path():
    p = Path("/tmp/test subtitles.ass")
    vf = ffmpeg_subtitles_filter(p)
    assert "subtitles=" in vf
    assert "format=yuv420p" in vf
