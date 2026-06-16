"""Tests for Facebook credential resolution."""

from __future__ import annotations

import json

from shorts_bot.integrations.facebook_credentials import (
    load_facebook_api_file,
    resolve_facebook_credentials,
    save_facebook_api_file,
)


def test_resolve_from_file(tmp_path, monkeypatch):
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
    save_facebook_api_file(page_id="111", page_access_token="EAAtest", page_name="Peripheral")
    pid, token, source = resolve_facebook_credentials()
    assert pid == "111"
    assert token == "EAAtest"
    assert source == "facebook_api.json"
    data = load_facebook_api_file()
    assert data["page_name"] == "Peripheral"


def test_resolve_env_wins(monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.integrations.facebook_credentials.settings.facebook_page_id",
        "222",
    )
    monkeypatch.setattr(
        "shorts_bot.integrations.facebook_credentials.settings.meta_page_access_token",
        "EAAenv",
    )
    pid, token, source = resolve_facebook_credentials()
    assert pid == "222"
    assert token == "EAAenv"
    assert source == "env"
