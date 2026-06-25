from shorts_bot.agents.duration import format_duration, parse_work_duration


def test_parse_bracket_hour():
    p = parse_work_duration("[1h] plan cosy shorts this week")
    assert p.work_seconds == 3600
    assert "plan cosy" in p.cleaned_message


def test_parse_take_an_hour():
    p = parse_work_duration("take an hour to respond — score attachment topics")
    assert p.work_seconds == 3600
    assert "attachment" in p.cleaned_message.lower()


def test_parse_dont_respond_for_minutes():
    p = parse_work_duration("don't respond for 30 minutes, research HFA hooks")
    assert p.work_seconds == 1800
    assert "HFA" in p.cleaned_message or "research" in p.cleaned_message.lower()


def test_parse_spend_45m():
    p = parse_work_duration("spend 45m on this: draft 3 cosy topics")
    assert p.work_seconds == 45 * 60


def test_parse_take_one_minute():
    p = parse_work_duration("take 1 minute to score topics")
    assert p.work_seconds == 60
    assert p.cleaned_message == "score topics"


def test_no_duration():
    p = parse_work_duration("draft a short about sunday couch dread")
    assert p.work_seconds is None
    assert p.cleaned_message == "draft a short about sunday couch dread"


def test_format_duration():
    assert format_duration(3600) == "1h"
    assert format_duration(90) == "90s"
    assert "m" in format_duration(300)
