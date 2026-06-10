from unittest.mock import patch

from shorts_bot.agents.manager import ChiefManager, should_use_manager
from shorts_bot.agents.runner import SpecialistRunner
from shorts_bot.agents.tasks import WorkLogEntry
from shorts_bot.agents.work_loop import WorkSession


def test_should_use_manager_with_duration():
    assert should_use_manager("take 10 minutes to plan topics")


def test_should_use_manager_with_prefix():
    assert should_use_manager("manager: score cosy niches")


def test_should_not_use_manager_plain():
    assert not should_use_manager("draft sleep tips")


def test_offline_manager_with_budget(monkeypatch):
    from shorts_bot.agents import work_loop

    def fake_run(user_request, budget_seconds, on_progress=None):
        s = WorkSession(budget_seconds=60, user_request=user_request)
        s.log.append(
            WorkLogEntry(
                task="score_topics",
                role="niche_strategist",
                summary="Scored 3 topics",
                elapsed_seconds=1.0,
                detail="done",
            )
        )
        return s

    monkeypatch.setattr("shorts_bot.agents.manager.run_timed_work", fake_run)

    with patch.object(SpecialistRunner, "available", False):
        result = ChiefManager().handle("take 1 minute to score topics")
        assert result.parsed.has_work_budget
        assert "score topics" in result.parsed.cleaned_message
        assert "offline" in result.reply.lower() or "Chief Manager" in result.reply
        assert result.session is not None
        assert len(result.session.log) >= 1
