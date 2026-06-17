"""Tests for Facebook Reel Graph API upload."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from shorts_bot.integrations.facebook_reel_api import probe_facebook_reel_api, upload_facebook_reel


def test_probe_missing_tokens(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "shorts_bot.integrations.facebook_credentials.settings.facebook_page_id",
        None,
    )
    monkeypatch.setattr(
        "shorts_bot.integrations.facebook_credentials.settings.meta_page_access_token",
        None,
    )
    monkeypatch.setattr(
        "shorts_bot.integrations.facebook_credentials.settings.data_dir",
        tmp_path,
    )
    ok, msg = probe_facebook_reel_api()
    assert ok is False
    assert "not set" in msg.lower()


def test_probe_ok(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.integrations.facebook_credentials.settings.facebook_page_id",
        "12345",
    )
    monkeypatch.setattr(
        "shorts_bot.integrations.facebook_credentials.settings.meta_page_access_token",
        "token",
    )

    class FakeResp:
        def read(self):
            return json.dumps({"name": "Peripheral", "id": "12345"}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    with patch("urllib.request.urlopen", return_value=FakeResp()):
        ok, msg = probe_facebook_reel_api()
    assert ok is True
    assert "Peripheral" in msg


def test_upload_three_phase(tmp_path, monkeypatch):
    video = tmp_path / "short.mp4"
    video.write_bytes(b"fake-mp4-bytes")
    monkeypatch.setattr(
        "shorts_bot.integrations.facebook_credentials.settings.facebook_page_id",
        "999",
    )
    monkeypatch.setattr(
        "shorts_bot.integrations.facebook_credentials.settings.meta_page_access_token",
        "page-token",
    )

    calls: list[tuple[str, dict]] = []

    def fake_post(url, data):
        calls.append((url, data))
        if data.get("upload_phase") == "start":
            return {"video_id": "vid1", "upload_url": "https://upload.example/vid1"}
        if data.get("upload_phase") == "finish":
            return {"post_id": "post1"}
        return {}

    with patch("shorts_bot.integrations.facebook_reel_api._post_form", side_effect=fake_post):
        with patch("shorts_bot.integrations.facebook_reel_api._upload_binary") as up:
            result = upload_facebook_reel(video, description="test hook")
    assert result.video_id == "vid1"
    assert result.post_id == "post1"
    assert up.called
    assert calls[0][1]["upload_phase"] == "start"
    assert calls[1][1]["upload_phase"] == "finish"


def test_upload_requires_tokens(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.integrations.facebook_credentials.settings.facebook_page_id",
        None,
    )
    monkeypatch.setattr(
        "shorts_bot.integrations.facebook_credentials.settings.meta_page_access_token",
        None,
    )
    monkeypatch.setattr(
        "shorts_bot.integrations.facebook_credentials.settings.data_dir",
        tmp_path,
    )
    video = tmp_path / "short.mp4"
    video.write_bytes(b"x")
    with pytest.raises(RuntimeError, match="FACEBOOK_PAGE_ID"):
        upload_facebook_reel(video, description="x")
