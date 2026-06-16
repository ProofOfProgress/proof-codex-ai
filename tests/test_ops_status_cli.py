from shorts_bot.config import Settings
from shorts_bot.production import ops_status_cli


def test_ops_status_handles_empty_database(tmp_path, monkeypatch):
    cfg = Settings(data_dir=tmp_path, database_path=tmp_path / "empty.db")
    monkeypatch.setattr(ops_status_cli, "settings", cfg)
    monkeypatch.setattr(
        ops_status_cli,
        "auth_status",
        lambda: {
            "credentials_configured": True,
            "token_saved": False,
            "ready": False,
        },
    )

    md = ops_status_cli.build_ops_status_markdown()

    assert "No approved drafts in queue" in md
    assert "No draft sample for guard check" in md
