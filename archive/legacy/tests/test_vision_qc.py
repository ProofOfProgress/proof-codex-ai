import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from shorts_bot.production.vision_qc import (
    VisionQCReport,
    pick_frame_times,
    run_vision_qc,
)


def test_pick_frame_times_uses_manifest(tmp_path):
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "manifest.json").write_text(
        json.dumps(
            {
                "segments": [
                    {"start_seconds": 0.0, "end_seconds": 3.0},
                    {"start_seconds": 3.0, "end_seconds": 7.0},
                    {"start_seconds": 7.0, "end_seconds": 12.0},
                    {"start_seconds": 12.0, "end_seconds": 20.0},
                ]
            }
        ),
        encoding="utf-8",
    )
    times = pick_frame_times(25.0, pack, max_frames=5)
    assert len(times) <= 5
    assert times[0] == 0.8


def test_run_vision_qc_local_frozen_frames(tmp_path, monkeypatch):
    from shorts_bot.config import Settings

    pack = tmp_path / "pack"
    pack.mkdir()
    video = pack / "final_short.mp4"
    video.write_bytes(b"not a real video but exists" * 100)

    fake = Settings(
        vision_qc_enabled=True,
        vision_qc_blocks_upload=True,
        gemini_api_key="x" * 24,
        vision_qc_max_frames=3,
    )
    monkeypatch.setattr("shorts_bot.production.vision_qc.settings", fake)

    same = b"\xff" * 2000
    frames_dir = pack / "qc_frames"
    frames_dir.mkdir()
    for i in range(3):
        (frames_dir / f"f{i}.jpg").write_bytes(same)

    with (
        patch("shorts_bot.production.vision_qc._probe_duration", return_value=30.0),
        patch("shorts_bot.production.vision_qc.pick_frame_times", return_value=[0.8, 5.0, 10.0]),
        patch("shorts_bot.production.vision_qc._extract_frame"),
    ):
        # Pretend extract wrote identical files
        def fake_extract(_video, t, out, **_kw):
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(same)

        monkeypatch.setattr("shorts_bot.production.vision_qc._extract_frame", fake_extract)
        report = run_vision_qc(video, pack, topic="test", hook="hook", use_cache=False)

    assert not report.passed
    assert report.skipped_gemini
    assert any("frozen" in i.lower() or "identical" in i.lower() for i in report.issues)


def test_run_vision_qc_gemini_pass(tmp_path, monkeypatch):
    from shorts_bot.config import Settings

    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "manifest.json").write_text(
        json.dumps({"segments": [{"start_seconds": 0, "end_seconds": 5}]}),
        encoding="utf-8",
    )
    video = pack / "final_short.mp4"
    video.write_bytes(b"video" * 500)

    fake = Settings(
        vision_qc_enabled=True,
        vision_qc_min_score=7.0,
        gemini_api_key="a" * 24,
        gemini_model="gemini-2.5-flash-lite",
        vision_qc_max_frames=2,
    )
    monkeypatch.setattr("shorts_bot.production.vision_qc.settings", fake)

    def fake_extract(_video, t, out, **_kw):
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(bytes([50 + int(t * 10)]) * 3000)

    mock_resp = MagicMock()
    mock_resp.choices = [
        MagicMock(
            message=MagicMock(
                content='{"score":8.5,"pass":true,"issues":[],"warnings":[],"hook_clear":true,"captions_safe":true,"figure_visible":true}'
            )
        )
    ]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_resp
    mock_backend = MagicMock(client=mock_client, model="gemini-2.5-flash-lite", provider="gemini")

    with (
        patch("shorts_bot.production.vision_qc._probe_duration", return_value=40.0),
        patch("shorts_bot.production.vision_qc._extract_frame", fake_extract),
        patch("shorts_bot.llm.provider.get_llm_backend", return_value=mock_backend),
    ):
        report = run_vision_qc(video, pack, topic="calm topic", hook="The minute before", use_cache=False)

    assert report.passed
    assert report.score >= 8.0
    assert (pack / "vision_qc.json").exists()
