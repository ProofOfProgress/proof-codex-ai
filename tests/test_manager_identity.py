from shorts_bot.agents.identity import manager_intro_line, manager_name
from shorts_bot.agents.roles import CHIEF_MANAGER


def test_manager_name_default():
    assert manager_name() == "AlphaBeta001"


def test_manager_intro_mentions_channel_not_as_manager_name():
    line = manager_intro_line()
    assert "AlphaBeta001" in line
    assert "Don't Blink" in line


def test_chief_manager_prompt_uses_agent_name():
    assert "AlphaBeta001" in CHIEF_MANAGER.system_prompt
    assert "NOT the channel" in CHIEF_MANAGER.system_prompt
