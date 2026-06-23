"""Tests for Zernio upload client."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from shorts_bot.zernio.client import account_id_for, credentials_configured
from shorts_bot.zernio.upload import upload_video


def test_credentials_configured(monkeypatch):
    from shorts_bot.config import settings

    monkeypatch.setattr(settings, "zernio_api_key", "sk_test123")
    assert credentials_configured() is True


def test_account_id_for_platform(monkeypatch):
    from shorts_bot.config import settings

    monkeypatch.setattr(settings, "zernio_api_key", "sk_test")
    monkeypatch.setattr(
        "shorts_bot.zernio.client.list_accounts",
        lambda: [{"platform": "tiktok", "_id": "acc_tiktok", "isActive": True, "enabled": True}],
    )
    assert account_id_for("tiktok") == "acc_tiktok"


def test_upload_video_builds_post(monkeypatch, tmp_path: Path):
    from shorts_bot.config import settings

    video = tmp_path / "clip.mp4"
    video.write_bytes(b"\x00" * 64)

    monkeypatch.setattr(settings, "zernio_api_key", "sk_test")
    monkeypatch.setattr(settings, "zernio_post_tiktok", True)
    monkeypatch.setattr(settings, "zernio_post_facebook", False)
    monkeypatch.setattr(settings, "zernio_tiktok_account_id", "tiktok123")

    with patch("shorts_bot.zernio.upload.presign_video", return_value=("https://up", "https://pub")):
        with patch("shorts_bot.zernio.upload.upload_file_to_presigned") as put:
            with patch(
                "shorts_bot.zernio.upload._request",
                return_value={"post": {"_id": "post1", "status": "published", "platforms": []}},
            ) as req:
                result = upload_video(video, caption="Hello #test")
                put.assert_called_once()
                req.assert_called_once()
                body = req.call_args.kwargs["json"]
                assert body["content"] == "Hello #test"
                assert body["platforms"][0]["accountId"] == "tiktok123"
                assert result.post_id == "post1"
