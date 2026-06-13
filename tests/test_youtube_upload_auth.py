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


def test_oauth_url_pending_state_is_json(tmp_path, monkeypatch):
    from shorts_bot.youtube import google_auth

    pending = tmp_path / "oauth_flow.json"
    monkeypatch.setattr(google_auth, "OAUTH_FLOW_STATE", pending)

    flows = []
    saved = {}

    class FakeCreds:
        pass

    class FakeFlow:
        def __init__(self, state=None):
            self.state = state
            self.redirect_uri = None
            self.credentials = FakeCreds()
            self.authorization_response = None

        def authorization_url(self, **_kwargs):
            return "https://accounts.example.test/auth", "state-123"

        def fetch_token(self, *, authorization_response):
            self.authorization_response = authorization_response

    def fake_make_flow(*, state=None):
        flow = FakeFlow(state=state)
        flows.append(flow)
        return flow

    def fake_save_credentials(creds, *, scopes=None):
        saved["creds"] = creds
        saved["scopes"] = scopes

    monkeypatch.setattr(google_auth, "_make_flow", fake_make_flow)
    monkeypatch.setattr(google_auth, "save_credentials", fake_save_credentials)

    url = google_auth.oauth_authorization_url()
    assert url == "https://accounts.example.test/auth"
    assert pending.exists()
    assert "state-123" in pending.read_text(encoding="utf-8")

    result = google_auth.oauth_complete_redirect("http://127.0.0.1:8090/?code=abc")

    assert result["ok"]
    assert flows[1].state == "state-123"
    assert flows[1].authorization_response.endswith("code=abc")
    assert saved["creds"] is flows[1].credentials
    assert "https://www.googleapis.com/auth/youtube.upload" in saved["scopes"]
    assert not pending.exists()
