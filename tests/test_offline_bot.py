from pathlib import Path

from shorts_bot.approval.queue import ApprovalQueue
from shorts_bot.bot.agent import ShortsBotAgent
from shorts_bot.bot.tools import ToolRunner
from shorts_bot.drafts.generator import DraftGenerator
from shorts_bot.memory.store import MemoryStore


def test_offline_draft_command(tmp_path: Path):
    store = MemoryStore(tmp_path / "test.db")
    generator = DraftGenerator(store, client=None)
    queue = ApprovalQueue(store)
    tools = ToolRunner(store, generator, queue)
    agent = ShortsBotAgent(store, tools, client=None)

    reply = agent.chat("draft better mornings")
    assert "Created draft #1" in reply
    assert "pending" in agent.chat("pending").lower()
