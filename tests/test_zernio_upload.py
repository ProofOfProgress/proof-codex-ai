# Tests for Zernio upload (photo carousel + video)

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from shorts_bot.zernio.upload import upload_photo_carousel, upload_video


def test_upload_photo_carousel_requires_two_images(tmp_path: Path):
    one = tmp_path / "a.png"
    one.write_bytes(b"fake")
    with pytest.raises(ValueError, match="at least 2"):
        upload_photo_carousel([one], title="t")


def test_upload_photo_carousel_payload(tmp_path: Path):
    s1 = tmp_path / "hook.png"
    s2 = tmp_path / "cta.png"
    s1.write_bytes(b"png1")
    s2.write_bytes(b"png2")

    with (
        patch("shorts_bot.zernio.upload.credentials_configured", return_value=True),
        patch("shorts_bot.zernio.upload.presign_media", side_effect=[
            ("https://up/1", "https://cdn/1"),
            ("https://up/2", "https://cdn/2"),
        ]),
        patch("shorts_bot.zernio.upload.upload_file_to_presigned") as up,
        patch("shorts_bot.zernio.upload._request") as req,
    ):
        req.return_value = {"post": {"_id": "post123", "status": "published"}}
        result = upload_photo_carousel(
            [s1, s2],
            title="FROG BUBBLE WRAP ASMR",
            caption="#asmr #fyp",
            tiktok_account_id="acct_abc",
            private=True,
        )

    assert result.post_id == "post123"
    assert up.call_count == 2
    payload = req.call_args.kwargs["json"]
    assert payload["mediaItems"] == [
        {"type": "image", "url": "https://cdn/1"},
        {"type": "image", "url": "https://cdn/2"},
    ]
    assert payload["platforms"] == [{"platform": "tiktok", "accountId": "acct_abc"}]
    assert payload["tiktokSettings"]["media_type"] == "photo"
    assert payload["tiktokSettings"]["privacy_level"] == "SELF_ONLY"
    assert payload["tiktokSettings"]["description"] == "#asmr #fyp"


def test_upload_video_with_account_id(tmp_path: Path):
    vid = tmp_path / "clip.mp4"
    vid.write_bytes(b"mp4")

    with (
        patch("shorts_bot.zernio.upload.credentials_configured", return_value=True),
        patch("shorts_bot.zernio.upload.presign_video", return_value=("https://up/v", "https://cdn/v")),
        patch("shorts_bot.zernio.upload.upload_file_to_presigned"),
        patch("shorts_bot.zernio.upload._request") as req,
    ):
        req.return_value = {"post": {"_id": "vid99", "status": "published"}}
        result = upload_video(
            vid,
            caption="caption",
            tiktok=True,
            facebook=False,
            tiktok_account_id="zid_1",
            private=True,
        )

    payload = req.call_args.kwargs["json"]
    assert payload["platforms"] == [{"platform": "tiktok", "accountId": "zid_1"}]
    assert payload["tiktokSettings"]["privacy_level"] == "SELF_ONLY"
    assert result.post_id == "vid99"
