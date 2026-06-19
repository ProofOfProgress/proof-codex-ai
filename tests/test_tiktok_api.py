from unittest.mock import MagicMock, patch

from shorts_bot.tiktok.oauth import (
    oauth_authorization_url,
    oauth_complete_code,
    redirect_uri,
    requested_scopes,
)


def test_oauth_url_contains_client_key(monkeypatch):
    from shorts_bot.config import Settings

    fake = Settings(
        tiktok_client_key="test_client_key_123",
        tiktok_client_secret="test_secret_456",
    )
    monkeypatch.setattr("shorts_bot.tiktok.oauth.settings", fake)
    url = oauth_authorization_url(code_challenge="abc123")
    assert "test_client_key_123" in url
    assert "video.publish" in url
    assert "code_challenge=abc123" in url
    assert "8091" in url or redirect_uri() in url


def test_generate_pkce_pair():
    from shorts_bot.tiktok.oauth import generate_pkce_pair

    verifier, challenge = generate_pkce_pair()
    assert 43 <= len(verifier) <= 128
    import hashlib

    assert challenge == hashlib.sha256(verifier.encode("utf-8")).hexdigest()


def test_requested_scopes_default():
    scopes = requested_scopes()
    assert "user.info.basic" in scopes
    assert "video.publish" in scopes


def test_oauth_complete_code_saves_token(tmp_path, monkeypatch):
    from shorts_bot.config import Settings

    token_file = tmp_path / "tiktok_token.json"
    fake = Settings(
        tiktok_client_key="key",
        tiktok_client_secret="sec",
        tiktok_token_path=token_file,
    )
    monkeypatch.setattr("shorts_bot.tiktok.oauth.settings", fake)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "access_token": "act.test",
        "refresh_token": "rft.test",
        "open_id": "oid",
        "scope": "user.info.basic,video.publish",
        "expires_in": 86400,
    }

    with patch("shorts_bot.tiktok.oauth.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.post.return_value = mock_resp
        result = oauth_complete_code("authcode123")

    assert result["ok"] is True
    assert token_file.exists()
    assert "act.test" in token_file.read_text()


def test_upload_video_init_and_put(tmp_path, monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.tiktok import upload as tt_upload

    video = tmp_path / "short.mp4"
    video.write_bytes(b"\x00" * 1000)

    token_file = tmp_path / "tok.json"
    token_file.write_text(
        '{"access_token":"tok","scope":"video.publish","refresh_token":"r"}',
        encoding="utf-8",
    )
    fake = Settings(
        tiktok_client_key="k",
        tiktok_client_secret="s",
        tiktok_token_path=token_file,
        tiktok_declare_aigc=True,
    )
    monkeypatch.setattr("shorts_bot.tiktok.oauth.settings", fake)
    monkeypatch.setattr("shorts_bot.tiktok.upload.settings", fake)

    def fake_post(url, **kwargs):
        resp = MagicMock()
        resp.status_code = 200
        if "creator_info" in url:
            resp.json.return_value = {
                "data": {"privacy_level_options": ["PUBLIC_TO_EVERYONE", "SELF_ONLY"]},
                "error": {"code": "ok", "message": ""},
            }
        elif "video/init" in url:
            resp.json.return_value = {
                "data": {
                    "publish_id": "pub123",
                    "upload_url": "https://upload.example/put",
                },
                "error": {"code": "ok", "message": ""},
            }
        elif "status/fetch" in url:
            resp.json.return_value = {
                "data": {"status": "PUBLISH_COMPLETE"},
                "error": {"code": "ok", "message": ""},
            }
        return resp

    def fake_put(url, **kwargs):
        resp = MagicMock()
        resp.status_code = 200
        resp.text = ""
        return resp

    with patch("shorts_bot.tiktok.upload.httpx.Client") as client_cls:
        client = client_cls.return_value.__enter__.return_value
        client.post.side_effect = fake_post
        client.put.side_effect = fake_put
        result = tt_upload.upload_video(video, title="Test #ai")

    assert result.publish_id == "pub123"
    assert result.status == "PUBLISH_COMPLETE"
