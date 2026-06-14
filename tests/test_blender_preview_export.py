"""Tests for Blender preview export."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.blender.preview_export import export_preview_assets


def test_export_preview_assets_writes_watch_md(tmp_path):
    pack = tmp_path / "draft_1"
    clips = pack / "clips"
    clips.mkdir(parents=True)
    # Minimal fake mp4 (not valid video but ffmpeg may still fail gracefully)
    (pack / "final_short.mp4").write_bytes(b"\x00" * 200)
    (clips / "blender_part_01.mp4").write_bytes(b"\x00" * 200)
    watch = export_preview_assets(pack, draft_id=1)
    assert watch.is_file()
    text = watch.read_text()
    assert "draft #1" in text
    assert "Google Drive" in text
