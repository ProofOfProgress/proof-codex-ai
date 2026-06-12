def test_auth_status_upload_ready_flag(monkeypatch, tmp_path):
    from shorts_bot.config import Settings
    from shorts_bot.youtube import google_auth

    token = tmp_path / "token.json"
    fake = Settings(
        google_client_id="cid.apps.googleusercontent.com",
        google_client_secret="secret",
        youtube_token_path=token,
    )
    monkeypatch.setattr("shorts_bot.youtube.google_auth.settings", fake)

    st = google_auth.auth_status()
    assert st["credentials_configured"]
    assert not st["token_saved"]
    assert not st["upload_ready"]
