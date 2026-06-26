"""Shared FastAPI dependencies for TikTok Shop + self-learning."""

from __future__ import annotations

from shorts_bot.config import settings
from shorts_bot.memory.agent_memory import AgentMemoryStore, get_agent_memory_store
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.rewards.engine import RewardEngine
from shorts_bot.training.proposer import ImprovementProposer

_store: MemoryStore | None = None
_memory: MemoryExtensions | None = None
_agent_memory: AgentMemoryStore | None = None


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


def get_reward_engine() -> RewardEngine:
    return RewardEngine(get_memory())


def get_proposer() -> ImprovementProposer:
    try:
        from shorts_bot.llm.provider import get_llm_backend

        backend = get_llm_backend()
        client = backend.client if backend else None
        model = backend.model if backend else settings.openai_model
    except Exception:
        client = None
        model = settings.openai_model
    return ImprovementProposer(get_memory(), client=client, model=model)
