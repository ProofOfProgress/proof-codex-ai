import json

from shorts_bot.production.pack_health import assess_pack_health


def _write_manifest(pack, segments):
    (pack / "manifest.json").write_text(
        json.dumps(
            {
                "hook": "Your camera flagged motion.",
                "script": "Line one.\nLine two.",
                "segments": segments,
            }
        ),
        encoding="utf-8",
    )


def test_pack_health_ready_when_clips_and_audio_exist(tmp_path):
    pack = tmp_path / "draft_1"
    clips = pack / "clips"
    images = pack / "images"
    clips.mkdir(parents=True)
    images.mkdir(parents=True)
    (pack / "voiceover.mp3").write_bytes(b"\x00" * 200)
    (clips / "00.00.mp4").write_bytes(b"\x00" * 6000)
    (clips / "00.05.mp4").write_bytes(b"\x00" * 6000)
    (clips / "jumpscare_lunge.mp4").write_bytes(b"\x00" * 6000)
    _write_manifest(
        pack,
        [
            {"filename": "00.00.png", "spoken_text": "Motion flagged.", "start_seconds": 0},
            {"filename": "00.05.png", "spoken_text": "You turned.", "start_seconds": 5},
        ],
    )
    (pack / "content_stamp.json").write_text(
        json.dumps({"digest": "deadbeef"}),
        encoding="utf-8",
    )

    report = assess_pack_health(pack, draft_id=1)
    assert report.ready_to_render
    assert report.clip_count == 2
    assert report.missing_segment_count == 0


def test_pack_health_flags_missing_clip_and_still(tmp_path):
    pack = tmp_path / "draft_3"
    (pack / "clips").mkdir(parents=True)
    (pack / "images").mkdir(parents=True)
    (pack / "voiceover.mp3").write_bytes(b"\x00" * 200)
    _write_manifest(
        pack,
        [
            {"filename": "00.15.png", "spoken_text": "Lag beat.", "start_seconds": 15},
        ],
    )

    report = assess_pack_health(pack, draft_id=3)
    assert not report.ready_to_render
    assert report.missing_segment_count == 1
    assert any("00.15" in issue for issue in report.issues)


def test_pack_health_warns_on_still_fallback(tmp_path):
    pack = tmp_path / "draft_2"
    images = pack / "images"
    images.mkdir(parents=True)
    (pack / "clips").mkdir()
    (pack / "voiceover.mp3").write_bytes(b"\x00" * 200)
    (images / "00.04.png").write_bytes(b"\x00" * 100)
    _write_manifest(
        pack,
        [
            {"filename": "00.04.png", "spoken_text": "Still only.", "start_seconds": 4},
        ],
    )

    # draft_id=3 → suspense_replay (no dedicated jumpscare clip required)
    report = assess_pack_health(pack, draft_id=3)
    assert report.ready_to_render
    assert report.still_fallback_count == 1
    assert any("still" in w.lower() for w in report.warnings)
