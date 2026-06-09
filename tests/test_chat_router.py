from shorts_bot.services.chat_router import is_sync_command, parse_dev_request


def test_parse_dev_colon():
    r = parse_dev_request("dev: Polish UI | add glow effects")
    assert r == ("Polish UI", "add glow effects")


def test_parse_build_natural():
    r = parse_dev_request("build a dark mode toggle")
    assert r is not None
    assert "dark mode" in r[0].lower() or "dark mode" in r[1].lower()


def test_sync_commands():
    assert is_sync_command("sync")
    assert is_sync_command("sync youtube")
    assert not is_sync_command("syncopation")
