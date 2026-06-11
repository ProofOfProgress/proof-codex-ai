import json
from pathlib import Path

from shorts_bot.production.turboscribe_parser import TranscriptSegment
from shorts_bot.production.video_prompt_pack import (
    export_from_manifest,
    hook_only_prompt,
    write_video_prompt_pack,
)


def test_write_video_prompt_pack_creates_files(tmp_path: Path):
    segs = [
        TranscriptSegment(0.0, "Thumb hovers over phone on couch.", "00.00"),
        TranscriptSegment(4.0, "Three slow breaths.", "00.04"),
    ]
    payload = write_video_prompt_pack(
        tmp_path,
        segs,
        topic="Sunday phone check from the couch",
        total_duration=10.0,
        hybrid_hook=True,
    )
    assert (tmp_path / "video_prompts.json").exists()
    assert (tmp_path / "AI_VIDEO_HOOK.md").exists()
    assert (tmp_path / "video_prompts" / "00.00.txt").exists()
    assert payload["hybrid_hook"] is True
    assert payload["clips"][0]["ai_video_hero"] is True


def test_export_from_manifest(tmp_path: Path):
    manifest = {
        "topic": "the minute before you check your phone from the couch on Sunday",
        "visual_style": "ai_video",
        "segments": [
            {
                "start_seconds": 0.0,
                "end_seconds": 3.0,
                "filename": "00.00.png",
                "spoken_text": "I used to get stuck there.",
            },
            {
                "start_seconds": 3.0,
                "end_seconds": 8.0,
                "filename": "00.03.png",
                "spoken_text": "Phone in hand, dread building.",
            },
        ],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    payload = export_from_manifest(tmp_path, hybrid_hook=True)
    assert payload["hook_template_id"] == "sunday_couch_phone"
    assert len(payload["clips"]) == 2


def test_hook_only_prompt_matches_sunday():
    p = hook_only_prompt(
        "the minute before you check your phone from the couch on Sunday",
        "Thumb hovers.",
    )
    assert "SUBJECT:" in p
    assert "END STATE:" in p
