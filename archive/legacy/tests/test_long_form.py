import json
from pathlib import Path

from shorts_bot.production.long_quality import assess_long_quality
from shorts_bot.production.long_upload_meta import (
    build_long_compilation_package,
    chapters_from_manifest,
    format_chapter_block,
)
from shorts_bot.production.script_expand import expand_short_to_long_outline
from shorts_bot.production.short_video_resolver import is_qa_build_filename, resolve_final_short_video


def test_resolve_prefers_non_qa_build(tmp_path: Path):
    (tmp_path / "final_short_sync_test.mp4").write_bytes(b"x" * 10000)
    good = tmp_path / "final_short_v21_cctv.mp4"
    good.write_bytes(b"x" * 10000)
    resolved = resolve_final_short_video(tmp_path)
    assert resolved == good


def test_is_qa_build_filename():
    assert is_qa_build_filename("final_short_sync_test.mp4")
    assert not is_qa_build_filename("final_short_v21_cctv.mp4")


def test_chapters_from_manifest():
    manifest = {
        "segments": [
            {"hook": "You live alone", "duration_seconds": 26},
            {"hook": "The mirror blinked", "duration_seconds": 30},
        ]
    }
    chapters = chapters_from_manifest(manifest)
    assert len(chapters) == 2
    assert chapters[1].start_seconds == 26.0
    block = format_chapter_block(chapters)
    assert "0:00" in block
    assert "0:26" in block


def test_build_long_compilation_package_title():
    pkg = build_long_compilation_package(
        story_count=3,
        chapters=[],
        hooks=["You hear a knock at 3 AM"],
    )
    assert "3 scary stories" in pkg.title
    assert "Peripheral" in pkg.title
    assert "don't blink" in pkg.description


def test_script_expand_outline_sections():
    outline = expand_short_to_long_outline(
        draft_id=3,
        topic="Security camera",
        hook="You check the feed at 3:12 AM.",
        script="You check the feed at 3:12 AM. Someone is in the hall. You lock the door.",
        target_words=1000,
    )
    assert outline.draft_id == 3
    assert len(outline.sections) >= 5
    assert outline.sections[0]["id"] == "hook"


def test_long_quality_fails_without_manifest(tmp_path: Path):
    report = assess_long_quality(tmp_path)
    assert not report.passed
    assert any("manifest" in i.lower() for i in report.issues)


def test_long_quality_compilation_segment_count(tmp_path: Path):
    pack = tmp_path / "long_compilation_001"
    pack.mkdir()
    (pack / "final_long.mp4").write_bytes(b"\x00" * 100_000)
    manifest = {
        "format": "long_compilation",
        "output_video": "final_long.mp4",
        "total_duration_seconds": 80,
        "segments": [
            {"draft_id": 2, "duration_seconds": 26, "hook": "a"},
            {"draft_id": 3, "duration_seconds": 27, "hook": "b"},
        ],
    }
    (pack / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    report = assess_long_quality(pack)
    assert not report.passed
    assert any("3" in i for i in report.issues)
