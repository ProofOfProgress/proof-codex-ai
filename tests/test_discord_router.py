from shorts_bot.services.chat_router import (
    is_daily_command,
    is_login_status_command,
    parse_daily_topic,
    parse_research_request,
)


def test_daily_commands():
    assert is_daily_command("daily")
    assert is_daily_command("run daily")
    assert parse_daily_topic("daily the minute before a talk") == "the minute before a talk"
    assert parse_daily_topic("daily") is None


def test_research_command():
    assert parse_research_request("research hard conversation") == "hard conversation"


def test_login_status_command():
    assert is_login_status_command("login status")
    assert is_login_status_command("health")
