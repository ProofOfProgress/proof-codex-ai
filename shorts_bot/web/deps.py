from __future__ import annotations

from openai import OpenAI

from shorts_bot.approval.queue import ApprovalQueue
from shorts_bot.bot.agent import ShortsBotAgent
from shorts_bot.bot.tools import ToolRunner
from shorts_bot.config import settings
from shorts_bot.course.loader import CourseKnowledgeBase
from shorts_bot.course.router import CourseRouter
from shorts_bot.drafts.generator import DraftGenerator
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.rewards.engine import RewardEngine
from shorts_bot.training.proposer import ImprovementProposer


_store: MemoryStore | None = None
_memory: MemoryExtensions | None = None
_agent: ShortsBotAgent | None = None


def get_store() -> MemoryStore:
    global _store
    if _store is None:
        _store = MemoryStore(settings.database_path)
    return _store


def get_memory() -> MemoryExtensions:
    global _memory
    if _memory is None:
        _memory = MemoryExtensions(get_store())
    return _memory


def get_agent() -> ShortsBotAgent:
    global _agent
    if _agent is not None:
        wants_openai = settings.has_openai
        has_openai = _agent.client is not None
        if wants_openai != has_openai:
            _agent = None
        else:
            return _agent
    store = get_store()
    kb = CourseKnowledgeBase(settings.course_dir)
    router = CourseRouter(kb)
    client = OpenAI(api_key=settings.openai_api_key) if settings.has_openai else None
    memory = get_memory()
    generator = DraftGenerator(store, client=client, router=router, memory=memory)
    queue = ApprovalQueue(store)
    tools = ToolRunner(store, generator, queue, router=router)
    _agent = ShortsBotAgent(store, tools, client, router, kb)
    return _agent


def get_reward_engine() -> RewardEngine:
    return RewardEngine(get_memory())


def get_proposer() -> ImprovementProposer:
    client = OpenAI(api_key=settings.openai_api_key) if settings.has_openai else None
    return ImprovementProposer(get_memory(), client=client)


def get_analytics_sync():
    from shorts_bot.youtube.sync import AnalyticsSync

    return AnalyticsSync(get_memory(), get_proposer())
