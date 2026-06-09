from pathlib import Path

from shorts_bot.course.loader import CourseKnowledgeBase
from shorts_bot.course.router import CourseRouter


def test_knowledge_base_loads_nine_files():
    kb = CourseKnowledgeBase(Path("course"))
    assert len(kb.all_files()) == 9
    assert kb.get("02") is not None
    assert "hook" in kb.get("02").content.lower()


def test_router_picks_retention_for_script_question():
    kb = CourseKnowledgeBase(Path("course"))
    router = CourseRouter(kb)
    result = router.route("my script pacing feels weak in the middle")
    assert "06" in result.files
    assert result.main_lever == "script / retention / payoff"


def test_router_picks_editing_for_capcut():
    kb = CourseKnowledgeBase(Path("course"))
    router = CourseRouter(kb)
    result = router.route("how do I edit faster in capcut")
    assert "08" in result.files


def test_free_services_mentions_capcut():
    kb = CourseKnowledgeBase(Path("course"))
    assert "CapCut" in kb.free_services
