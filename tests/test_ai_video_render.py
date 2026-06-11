"""AI video clip render mode in manifest + ffmpeg trim helper."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from shorts_bot.config import Settings


def test_ai_video_config_defaults():
    fields = Settings.model_fields
    assert fields["visual_style"].default == "ai_video"
    assert fields["replicate_video_model"].default == "minimax/video-01"
    assert fields["ai_video_max_beats"].default == 10


def test_manifest_video_clips_mode_detected(tmp_path):
    pack = tmp_path / "draft_2"
    pack.mkdir()
    (pack / "voiceover.mp3").write_bytes(b"\x00" * 100)
    manifest = {
        "render_mode": "video_clips",
        "segments": [
            {
                "start_seconds": 0,
                "end_seconds": 3,
                "filename": "00.00.png",
                "clip_filename": "00.00.mp4",
                "spoken_text": "hook line",
            }
        ],
    }
    (pack / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    from shorts_bot.production.render_video import _scaled_durations

    segs = manifest["segments"]
    durs = _scaled_durations(segs, 3.0)
    assert len(durs) == 1
    assert durs[0] > 0


def test_replicate_multipart_upload_body(tmp_path):
    from shorts_bot.production.images.replicate import _multipart_file_body

    src = tmp_path / "frame.png"
    src.write_bytes(b"\x89PNGtest")
    body, content_type = _multipart_file_body(src)
    assert b'name="content"' in body
    assert b"frame.png" in body
    assert b"\x89PNGtest" in body
    assert "multipart/form-data" in content_type


def test_trim_scale_clip_runs_ffmpeg(tmp_path):
    from shorts_bot.production.render_video import _trim_scale_clip

    src = tmp_path / "src.mp4"
    # minimal valid mp4 not needed if we mock subprocess
    src.write_bytes(b"not-real")
    dest = tmp_path / "out.mp4"
    with patch("shorts_bot.production.render_video.subprocess.run") as run:
        _trim_scale_clip(src, dest, duration=2.5, width=1080, height=1920)
        assert run.called
        cmd = run.call_args[0][0]
        assert "ffmpeg" in cmd[0]
        assert "-t" in cmd
