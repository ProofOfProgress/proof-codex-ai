"""Tests for TikTok ADB carousel (Lead 3 — sound deep link)."""

from pathlib import Path

from shorts_bot.tiktok.adb_carousel import post_bubble_wrap_via_adb, status_dict
from shorts_bot.tiktok.sounds import (
    MACKENZIE_SOUND_ID,
    MACKENZIE_SOUND_URL,
    mackenzie_deep_link_uri,
    sound_deep_link_uri,
)


def test_mackenzie_deep_link_uri():
    assert sound_deep_link_uri(MACKENZIE_SOUND_ID) == f"tiktok://music/{MACKENZIE_SOUND_ID}"
    assert mackenzie_deep_link_uri() == f"tiktok://music/{MACKENZIE_SOUND_ID}"
    assert MACKENZIE_SOUND_ID in MACKENZIE_SOUND_URL


def test_dry_run_post_bubble_wrap(tmp_path: Path):
    slide1 = tmp_path / "hook.png"
    slide2 = tmp_path / "cta.png"
    slide1.write_bytes(b"png1")
    slide2.write_bytes(b"png2")

    result = post_bubble_wrap_via_adb(slide1, slide2, dry_run=True)
    assert result.ok
    assert result.sound_id == MACKENZIE_SOUND_ID
    assert any("DRY RUN" in step for step in result.steps)
    assert "tiktok://music" in result.steps[0]


def test_status_dict_without_adb(monkeypatch):
    from shorts_bot.tiktok.adb import AdbClient

    def fake_devices(self):  # noqa: ANN001
        return []

    monkeypatch.setattr(AdbClient, "devices", fake_devices)
    data = status_dict()
    assert data["adb_available"] is True
    assert data["devices"] == []
    assert MACKENZIE_SOUND_ID in data["mackenzie_uri"]
