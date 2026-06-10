from unittest.mock import MagicMock, patch

from shorts_bot.agents.priority import WorkPriority, user_wants_drafts, user_wants_research
from shorts_bot.agents.underlings.team import UnderlingTeam
from shorts_bot.agents.work_loop import run_timed_work


def test_user_wants_research():
    assert user_wants_research("plan cosy topics this week")
    assert not user_wants_drafts("plan cosy topics this week")


def test_user_wants_drafts():
    assert user_wants_drafts("draft a short about sunday couch dread")
    assert not user_wants_drafts("research attachment hooks")


def test_research_priority_skips_draft(monkeypatch):
    monkeypatch.setattr("shorts_bot.config.settings.manager_work_priority", "research")

    class FakeTeam:
        def __init__(self, **kwargs):
            self.plan_called = False

        def plan_session(self, user_request, budget_seconds):
            self.plan_called = True
            from shorts_bot.agents.tasks import WorkLogEntry

            return WorkLogEntry("plan", "research_lead", "planned", 0, "plan")

        def score_topics_batch(self, user_request, *, offset=0, count=5):
            from shorts_bot.agents.tasks import WorkLogEntry

            return WorkLogEntry(
                "score_topics",
                "niche_strategist",
                "scored",
                1.0,
                "scores",
                artifacts={"topics": ["topic a"]},
            )

        def research_topic_full(self, topic, *, user_request=""):
            from shorts_bot.agents.tasks import WorkLogEntry

            return [
                WorkLogEntry(
                    "deep_research",
                    "deep_research_worker",
                    f"deep {topic}",
                    2.0,
                    "detail",
                    artifacts={"topic": topic, "research_file": "data/research/t.json"},
                )
            ]

        def research_topic_deep(self, topic, *, user_request=""):
            from shorts_bot.agents.tasks import WorkLogEntry

            return WorkLogEntry(
                "deep_research",
                "deep_research_worker",
                f"deep {topic}",
                1.0,
                "d",
                artifacts={"topic": topic},
            )

        def maybe_write_draft(self, *args, **kwargs):
            raise AssertionError("draft should not run in research priority without explicit ask")

        def maybe_review(self, *args, **kwargs):
            return None

    monkeypatch.setattr("shorts_bot.agents.work_loop.UnderlingTeam", FakeTeam)

    session = run_timed_work("plan cosy shorts", 90, priority=WorkPriority.RESEARCH)
    assert session.priority == WorkPriority.RESEARCH
    assert any(e.task == "deep_research" for e in session.log)
    assert not any(e.task == "write_draft" for e in session.log)


def test_should_use_manager_research_delegate(monkeypatch):
    from shorts_bot.agents.manager import should_use_manager

    monkeypatch.setattr("shorts_bot.config.settings.manager_enabled", True)
    monkeypatch.setattr("shorts_bot.config.settings.manager_auto_delegate", True)
    assert should_use_manager("plan research for cosy couch topics")


def test_underling_team_no_draft_in_research_mode():
    team = UnderlingTeam(priority=WorkPriority.RESEARCH)
    assert team.maybe_write_draft("topic", user_request="plan hooks", research_detail="") is None


def test_underling_team_draft_when_explicitly_asked():
    team = UnderlingTeam(priority=WorkPriority.RESEARCH)
    with patch.object(team.tasks, "write_draft") as mock_draft:
        from shorts_bot.agents.tasks import WorkLogEntry

        mock_draft.return_value = WorkLogEntry(
            "write_draft", "script_writer", "drafted", 1.0, "script"
        )
        entry = team.maybe_write_draft("topic", user_request="draft a short", research_detail="x")
        assert entry is not None
        mock_draft.assert_called_once()
