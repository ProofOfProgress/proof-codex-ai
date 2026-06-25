from shorts_bot.invideo.agent_one import _is_logged_in_url


def test_logged_in_url():
    assert _is_logged_in_url("https://ai.invideo.io/workspaces")
    assert _is_logged_in_url("https://ai.invideo.io/workspace/abc/v40-copilot")
    assert not _is_logged_in_url("https://ai.invideo.io/signup")


from shorts_bot.invideo.agent_one import _is_logged_in_url, probe_agent_one_session


def test_probe_import():
    assert callable(probe_agent_one_session)
