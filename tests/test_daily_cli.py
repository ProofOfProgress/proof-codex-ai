import sys


def test_daily_cli_upload_flag(monkeypatch):
    from shorts_bot.production import daily_cli

    called = {}

    def fake_run_daily(*, topic=None, upload=None):
        called["topic"] = topic
        called["upload"] = upload
        return "ok"

    monkeypatch.setattr(daily_cli, "run_daily", fake_run_daily)
    monkeypatch.setattr(sys, "argv", ["daily_cli", "--topic", "security camera", "--upload"])

    daily_cli.main()

    assert called == {"topic": "security camera", "upload": True}
