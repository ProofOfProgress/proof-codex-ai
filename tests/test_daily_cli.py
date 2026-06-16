from shorts_bot.production import daily_cli


def test_daily_cli_upload_flag(monkeypatch):
    seen = {}

    def fake_run_daily(*, topic=None, upload=None):
        seen["topic"] = topic
        seen["upload"] = upload
        return "ok"

    monkeypatch.setattr(daily_cli, "run_daily", fake_run_daily)
    monkeypatch.setattr("sys.argv", ["daily_cli", "--topic", "closet camera", "--upload"])

    daily_cli.main()

    assert seen == {"topic": "closet camera", "upload": True}
