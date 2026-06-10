from shorts_bot.production.script_segments import segments_from_script
from shorts_bot.production.segment_sync import merge_segments_for_visual_cuts, resolve_segments
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


def test_resolve_segments_turboscribe_text():
    text = "0:00 The hook line.\n0:05 Second beat here.\n0:12 Third line now."
    segs, source = resolve_segments(
        script="ignored",
        pack_dir=__import__("pathlib").Path("/tmp/empty_pack"),
        turboscribe_text=text,
    )
    assert source == "turboscribe"
    assert len(segs) >= 2
