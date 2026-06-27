# Tests — Zernio photo carousel upload

from pathlib import Path
from unittest.mock import patch

from shorts_bot.zernio.upload import upload_photo_carousel


def test_upload_photo_carousel_builds_image_payload(tmp_path, monkeypatch):
    img1 = tmp_path / "hook.png"
    img2 = tmp_path / "cta.png"
    img1.write_bytes(b"png1")
    img2.write_bytes(b"png2")

    calls: list[dict] = []

    def fake_presign(path: Path):
        return f"https://upload/{path.name}", f"https://cdn/{path.name}"

    def fake_upload(url, path, **kwargs):
        return None

    def fake_request(method, path, **kwargs):
        calls.append(kwargs.get("json") or {})
        return {"post": {"_id": "post-1", "status": "submitted"}, "platforms": []}

    monkeypatch.setattr("shorts_bot.zernio.upload.presign_media", fake_presign)
    monkeypatch.setattr("shorts_bot.zernio.upload.upload_file_to_presigned", fake_upload)
    monkeypatch.setattr("shorts_bot.zernio.upload._request", fake_request)
    monkeypatch.setattr("shorts_bot.zernio.upload.credentials_configured", lambda: True)
    monkeypatch.setattr("shorts_bot.zernio.upload._tiktok_platform_entry", lambda account_id=None: {"platform": "tiktok", "accountId": "acct-1"})
    monkeypatch.setattr("shorts_bot.zernio.upload.require_pre_publish", lambda *a, **k: None)

    result = upload_photo_carousel(
        [img1, img2],
        title="Orange ASMR",
        tiktok_account_id="acct-1",
    )

    assert result.post_id == "post-1"
    payload = calls[0]
    assert len(payload["mediaItems"]) == 2
    assert payload["mediaItems"][0]["type"] == "image"
    assert payload["tiktokSettings"]["media_type"] == "photo"
    assert payload["tiktokSettings"]["auto_add_music"] is False
    assert payload["tiktokSettings"]["video_made_with_ai"] is True
