def test_daily_cli_upload_flag(monkeypatch):
    from shorts_bot.production import daily_cli

    seen = {}

    def fake_run_daily(*, topic=None, upload=None):
        seen["topic"] = topic
        seen["upload"] = upload
        return "ok"

    monkeypatch.setattr(daily_cli, "run_daily", fake_run_daily)
    monkeypatch.setattr("sys.argv", ["daily_cli", "--topic", "sleep camera", "--upload"])

    daily_cli.main()

    assert seen == {"topic": "sleep camera", "upload": True}


def test_daily_cli_no_upload_flag(monkeypatch):
    from shorts_bot.production import daily_cli

    seen = {}

    def fake_run_daily(*, topic=None, upload=None):
        seen["upload"] = upload
        return "ok"

    monkeypatch.setattr(daily_cli, "run_daily", fake_run_daily)
    monkeypatch.setattr("sys.argv", ["daily_cli", "--no-upload"])

    daily_cli.main()

    assert seen == {"upload": False}
