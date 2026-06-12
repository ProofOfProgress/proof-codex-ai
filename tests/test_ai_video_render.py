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
    assert fields["replicate_video_model_jumpscare"].default == "minimax/hailuo-2.3-fast"
    assert fields["ai_video_max_beats"].default == 10


def test_replicate_i2v_model_routing():
    from shorts_bot.production.render_ai_video import replicate_i2v_model_for_clip

    assert "hailuo" in replicate_i2v_model_for_clip(template_id="jumpscare_lunge")
    assert replicate_i2v_model_for_clip(model_hint="veo") == "minimax/video-01"


def test_load_motion_prompt_from_video_prompt_pack(tmp_path):
    pack = tmp_path / "draft_3"
    pack.mkdir()
    vp = pack / "video_prompts"
    vp.mkdir()
    (vp / "00.28.txt").write_text("LUNGE PROMPT FROM PACK", encoding="utf-8")
    (pack / "video_prompts.json").write_text(
        json.dumps(
            {
                "clips": [
                    {
                        "filename_stem": "00.28",
                        "prompt_file": "video_prompts/00.28.txt",
                        "model_hint": "hailuo",
                        "template_id": "jumpscare_lunge",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    from shorts_bot.production.render_ai_video import _video_prompt_for_segment
    from shorts_bot.production.turboscribe_parser import TranscriptSegment

    prompt, hint, tmpl = _video_prompt_for_segment(
        TranscriptSegment(28.0, "lunge line", "00.28"),
        topic="security cam",
        clip_index=8,
        pack_dir=pack,
        filename_stem="00.28",
    )
    assert prompt == "LUNGE PROMPT FROM PACK"
    assert hint == "hailuo"
    assert tmpl == "jumpscare_lunge"


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
