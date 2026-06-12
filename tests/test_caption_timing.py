from pathlib import Path

from shorts_bot.production.caption_timing import resolve_caption_segments
from shorts_bot.production.subtitles import build_subtitles_from_voice_segments


def test_caption_segments_finer_than_visual(tmp_path):
    pack = tmp_path / "draft"
    pack.mkdir()
    (pack / "transcript.txt").write_text(
        "\n".join(
            [
                "0:01 Your security camera flagged motion",
                "0:02 at 3:12 AM.",
                "0:04 You live alone.",
                "0:05 You opened the app.",
                "0:06 The hallway was empty.",
            ]
        ),
        encoding="utf-8",
    )
    script = (
        "Your security camera flagged motion at 3:12 AM. "
        "You live alone. You opened the app. The hallway was empty."
    )
    caps = resolve_caption_segments(
        pack_dir=pack,
        script=script,
        audio_duration=10.0,
    )
    assert len(caps) >= 4
    joined = " ".join(c["spoken_text"] for c in caps)
    assert "flagged" in joined


def test_caption_timing_survives_visual_cut_change():
    """Caption for line 1 can extend past a 3s visual cut."""
    voice = [
        {"start_seconds": 0.0, "end_seconds": 4.5, "spoken_text": "Long opening line to read."},
        {"start_seconds": 4.5, "end_seconds": 10.0, "spoken_text": "Second line."},
    ]
    srt, _ = build_subtitles_from_voice_segments(voice, audio_duration=10.0)
    assert "00:00:04,500" in srt or "00:00:04," in srt


def test_more_captions_than_visual_segments(tmp_path):
    pack = tmp_path / "draft"
    pack.mkdir()
    transcript = "\n".join(f"0:{i:02d} Line {i}." for i in range(1, 12))
    (pack / "transcript.txt").write_text(transcript, encoding="utf-8")
    caps = resolve_caption_segments(
        pack_dir=pack,
        script=" ".join(f"Line {i}." for i in range(1, 12)),
        audio_duration=27.0,
    )
    assert len(caps) >= 10
