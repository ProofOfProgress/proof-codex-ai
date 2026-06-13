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


def test_credentials_status_placeholder(monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.youtube import google_auth

    fake = Settings(
        google_client_id="your-client-id.apps.googleusercontent.com",
        google_client_secret="your-client-secret",
    )
    monkeypatch.setattr("shorts_bot.youtube.google_auth.settings", fake)
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)
    monkeypatch.setenv(
        "CLOUD_AGENT_ALL_SECRET_NAMES",
        "GEMINI_API_KEY,RESEMBLE_API_KEY",
    )
    monkeypatch.setenv("CLOUD_AGENT_INJECTED_SECRET_NAMES", "GEMINI_API_KEY")

    msg = google_auth.credentials_status_message()
    assert "NOT sending" in msg or "not in this agent" in msg


def test_credentials_from_token_file(monkeypatch, tmp_path):
    from shorts_bot.config import Settings
    from shorts_bot.youtube import google_auth

    token = tmp_path / "youtube_token.json"
    token.write_text(
        '{"token":"t","refresh_token":"r","client_id":"123.apps.googleusercontent.com",'
        '"client_secret":"GOCSPX-real-secret"}',
        encoding="utf-8",
    )
    fake = Settings(
        google_client_id="your-client-id.apps.googleusercontent.com",
        google_client_secret="your-client-secret",
        youtube_token_path=token,
    )
    monkeypatch.setattr("shorts_bot.youtube.google_auth.settings", fake)

    assert google_auth.credentials_configured()
    assert "youtube_token.json" in google_auth.credentials_status_message()


def test_import_token_json(tmp_path, monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.youtube import google_auth

    token = tmp_path / "youtube_token.json"
    fake = Settings(youtube_token_path=token)
    monkeypatch.setattr("shorts_bot.youtube.google_auth.settings", fake)

    raw = '{"token": "abc", "refresh_token": "xyz"}'
    result = google_auth.import_token_json(raw)
    assert result["ok"]
    assert token.exists()
    assert "refresh_token" in token.read_text()
