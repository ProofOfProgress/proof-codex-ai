from shorts_bot.production.script_segments import segments_from_script
from shorts_bot.production.segment_sync import (
    merge_segments_for_visual_cuts,
    normalize_segment_timeline,
    normalize_transcript_segments,
    resolve_segments,
)
from shorts_bot.production.turboscribe_parser import TranscriptSegment


def test_merge_segments_combines_fine_grained_cuts():
    segs = [
        TranscriptSegment(0.0, "The minute I hide", "00.00"),
        TranscriptSegment(1.2, "in the bathroom", "00.01"),
        TranscriptSegment(2.5, "that's when I know", "00.02"),
        TranscriptSegment(4.0, "I'm overwhelmed.", "00.04"),
    ]
    merged = merge_segments_for_visual_cuts(segs, target_min_seconds=2.0)
    assert len(merged) < len(segs)
    assert "bathroom" in merged[0].text or "hide" in merged[0].text


def test_resolve_segments_script_duration(tmp_path):
    script = "Line one here. Line two follows. And three ends."
    pack = tmp_path / "pack"
    pack.mkdir()
    segments, source = resolve_segments(script=script, pack_dir=pack, audio_duration=30.0)
    assert source == "script_duration"
    assert len(segments) >= 3


def test_normalize_segment_timeline_shifts_and_scales():
    """Draft #3 bug: first segment at 1.0s, manifest end 33.384, audio 27.4s."""
    segments = [
        {"start_seconds": 1.0, "end_seconds": 5.0, "spoken_text": "line one"},
        {"start_seconds": 5.0, "end_seconds": 33.384, "spoken_text": "line two"},
    ]
    normed = normalize_segment_timeline(segments, 27.4)
    assert abs(normed[0]["start_seconds"] - 0.0) < 0.01
    assert abs(normed[-1]["end_seconds"] - 27.4) < 0.05


def test_normalize_transcript_segments():
    segs = [
        TranscriptSegment(1.0, "hook", "00.01"),
        TranscriptSegment(28.384, "scare", "00.28"),
    ]
    normed = normalize_transcript_segments(segs, 27.4)
    assert normed[0].start_seconds < 0.5
    assert normed[-1].start_seconds < 27.4


def test_resolve_segments_turboscribe_text():
    text = "0:00 The hook line.\n0:05 Second beat here.\n0:12 Third line now."
    segs, source = resolve_segments(
        script="ignored",
        pack_dir=__import__("pathlib").Path("/tmp/empty_pack"),
        turboscribe_text=text,
    )
    assert source == "turboscribe"
    assert len(segs) >= 2
