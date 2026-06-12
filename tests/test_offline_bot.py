from pathlib import Path

from pathlib import Path as P

from shorts_bot.approval.queue import ApprovalQueue
from shorts_bot.bot.agent import ShortsBotAgent
from shorts_bot.bot.tools import ToolRunner
from shorts_bot.course.loader import CourseKnowledgeBase
from shorts_bot.course.router import CourseRouter
from shorts_bot.drafts.generator import DraftGenerator
from shorts_bot.memory.store import MemoryStore


def _build_offline_agent(store: MemoryStore) -> ShortsBotAgent:
    kb = CourseKnowledgeBase(P("course"))
    router = CourseRouter(kb)
    generator = DraftGenerator(store, client=None, router=router)
    queue = ApprovalQueue(store)
    tools = ToolRunner(store, generator, queue, router=router)
    return ShortsBotAgent(store, tools, client=None, router=router, kb=kb)


def test_offline_draft_command(tmp_path: Path):
    store = MemoryStore(tmp_path / "test.db")
    agent = _build_offline_agent(store)

    reply = agent.chat("draft better mornings")
    assert "Created draft #1" in reply
    assert "pending" in agent.chat("pending").lower()
