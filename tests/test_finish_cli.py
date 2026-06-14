from shorts_bot.production import finish_cli


def test_finish_cli_reports_pipeline_blocker(monkeypatch, tmp_path):
    monkeypatch.setattr(finish_cli.settings, "database_path", tmp_path / "bot.db")

    def boom(*args, **kwargs):
        raise RuntimeError("beat sheet must be owner-approved")

    monkeypatch.setattr(finish_cli, "finish_draft_pipeline", boom)

    assert finish_cli.finish_draft(1) == (
        "Pipeline blocked: beat sheet must be owner-approved"
    )
