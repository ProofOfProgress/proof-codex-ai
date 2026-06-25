"""YouTube altered/synthetic (AI) disclosure on upload."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def test_upload_short_sets_contains_synthetic_media(tmp_path, monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.youtube import upload as yt_upload

    video = tmp_path / "short.mp4"
    video.write_bytes(b"fake")

    fake_settings = Settings(
        google_client_id="x" * 30 + ".apps.googleusercontent.com",
        google_client_secret="secret",
        youtube_declare_synthetic_media=True,
    )
    monkeypatch.setattr(yt_upload, "settings", fake_settings)

    captured: dict = {}

    class FakeRequest:
        def next_chunk(self):
            return None, {"id": "abc12345678"}

    with patch.object(yt_upload, "load_credentials_for_upload", return_value=object()):
        with patch("googleapiclient.discovery.build") as build:
            yt = MagicMock()
            build.return_value = yt
            yt.videos.return_value.insert.return_value = FakeRequest()

            yt_upload.upload_short(
                video,
                title="Test",
                description="Desc",
                tags=["tag"],
                visibility="public",
            )

            captured["body"] = yt.videos.return_value.insert.call_args.kwargs["body"]

    assert captured["body"]["status"]["containsSyntheticMedia"] is True


def test_upload_short_omits_flag_when_disabled(tmp_path, monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.youtube import upload as yt_upload

    video = tmp_path / "short.mp4"
    video.write_bytes(b"fake")

    fake_settings = Settings(
        google_client_id="x" * 30 + ".apps.googleusercontent.com",
        google_client_secret="secret",
        youtube_declare_synthetic_media=False,
    )
    monkeypatch.setattr(yt_upload, "settings", fake_settings)

    with patch.object(yt_upload, "load_credentials_for_upload", return_value=object()):
        with patch("googleapiclient.discovery.build") as build:
            yt = MagicMock()
            build.return_value = yt
            yt.videos.return_value.insert.return_value = MagicMock(
                next_chunk=lambda: (None, {"id": "abc12345678"})
            )

            yt_upload.upload_short(video, title="T", description="D", tags=[])

            body = yt.videos.return_value.insert.call_args.kwargs["body"]
            assert "containsSyntheticMedia" not in body["status"]
