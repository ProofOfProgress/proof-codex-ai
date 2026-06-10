from __future__ import annotations

from shorts_bot.approval.queue import ApprovalQueue
from shorts_bot.bot.agent import ShortsBotAgent
from shorts_bot.brand.loader import ChannelBrand
from shorts_bot.bot.tools import ToolRunner
from shorts_bot.config import settings
from shorts_bot.course.loader import CourseKnowledgeBase
from shorts_bot.course.router import CourseRouter
from shorts_bot.drafts.generator import DraftGenerator
from shorts_bot.memory.agent_memory import AgentMemoryStore, get_agent_memory_store
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.rewards.engine import RewardEngine
from shorts_bot.training.proposer import ImprovementProposer
from shorts_bot.llm.provider import get_llm_backend


_store: MemoryStore | None = None
_memory: MemoryExtensions | None = None
_agent_memory: AgentMemoryStore | None = None
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


def get_agent_memory() -> AgentMemoryStore:
    global _agent_memory
    if _agent_memory is None:
        _agent_memory = get_agent_memory_store(get_store())
    return _agent_memory


def get_agent() -> ShortsBotAgent:
    global _agent
    backend = get_llm_backend()
    if _agent is not None:
        has_client = _agent.client is not None
        wants_client = backend is not None
        if wants_client != has_client:
            _agent = None
        elif backend and (
            _agent.llm_model != backend.model or _agent.llm_provider != backend.provider
        ):
            _agent = None
        else:
            return _agent
    store = get_store()
    kb = CourseKnowledgeBase(settings.course_dir)
    router = CourseRouter(kb)
    client = backend.client if backend else None
    llm_model = backend.model if backend else settings.openai_model
    llm_provider = backend.provider if backend else "offline"
    memory = get_memory()
    agent_memory = get_agent_memory()
    generator = DraftGenerator(
        store,
        client=client,
        model=llm_model,
        router=router,
        memory=memory,
        agent_memory=agent_memory,
        brand=ChannelBrand(),
    )
    queue = ApprovalQueue(store)
    tools = ToolRunner(store, generator, queue, router=router)
    _agent = ShortsBotAgent(
        store,
        tools,
        client,
        router,
        kb,
        ChannelBrand(),
        agent_memory,
        memory,
        llm_model=llm_model,
        llm_provider=llm_provider,
    )
    return _agent


def get_reward_engine() -> RewardEngine:
    return RewardEngine(get_memory())


def get_proposer() -> ImprovementProposer:
    backend = get_llm_backend()
    return ImprovementProposer(
        get_memory(),
        client=backend.client if backend else None,
        model=backend.model if backend else settings.openai_model,
    )


def get_analytics_sync():
    from shorts_bot.youtube.sync import AnalyticsSync

    return AnalyticsSync(get_memory(), get_proposer())
