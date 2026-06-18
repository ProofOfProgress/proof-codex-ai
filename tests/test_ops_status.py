from __future__ import annotations


def test_ops_status_handles_empty_database(tmp_path, monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.production import ops_status_cli

    fake = Settings(data_dir=tmp_path, database_path=tmp_path / "empty.db")
    monkeypatch.setattr(ops_status_cli, "settings", fake)
    monkeypatch.setattr(
        ops_status_cli,
        "auth_status",
        lambda: {
            "credentials_configured": False,
            "token_saved": False,
        },
    )

    md = ops_status_cli.build_ops_status_markdown()

    assert "No draft sample for guard check" in md
    assert "YouTube auth" in md
