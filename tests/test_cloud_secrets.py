import os

from shorts_bot.cloud_secrets import youtube_secrets_audit, youtube_secrets_message


def test_youtube_secrets_missing_from_agent_list(monkeypatch):
    monkeypatch.setenv(
        "CLOUD_AGENT_ALL_SECRET_NAMES",
        "GEMINI_API_KEY,RESEMBLE_API_KEY,CURSOR_API_KEY",
    )
    monkeypatch.setenv("CLOUD_AGENT_INJECTED_SECRET_NAMES", "GEMINI_API_KEY,RESEMBLE_API_KEY")
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)

    audit = youtube_secrets_audit()
    assert audit["GOOGLE_CLIENT_ID"] == "missing"
    assert audit["GOOGLE_CLIENT_SECRET"] == "missing"

    msg = youtube_secrets_message()
    assert msg is not None
    assert "NOT sending" in msg
    assert "GOOGLE_CLIENT_ID" in msg


def test_youtube_token_json_present_skips_missing_google_keys(monkeypatch):
    monkeypatch.setenv("CLOUD_AGENT_ALL_SECRET_NAMES", "GEMINI_API_KEY")
    monkeypatch.setenv("YOUTUBE_TOKEN_JSON", '{"token":"x","refresh_token":"y","client_id":"a"}')

    msg = youtube_secrets_message()
    assert msg is None
