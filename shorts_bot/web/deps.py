from __future__ import annotations

from functools import lru_cache

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


@lru_cache
def get_store() -> MemoryStore:
    return MemoryStore(settings.database_path)


@lru_cache
def get_memory() -> MemoryExtensions:
    return MemoryExtensions(get_store())


@lru_cache
def get_agent() -> ShortsBotAgent:
    store = get_store()
    kb = CourseKnowledgeBase(settings.course_dir)
    router = CourseRouter(kb)
    client = OpenAI(api_key=settings.openai_api_key) if settings.has_openai else None
    generator = DraftGenerator(store, client=client, router=router)
    queue = ApprovalQueue(store)
    tools = ToolRunner(store, generator, queue, router=router)
    return ShortsBotAgent(store, tools, client, router, kb)


def get_reward_engine() -> RewardEngine:
    return RewardEngine(get_memory())


def get_proposer() -> ImprovementProposer:
    client = OpenAI(api_key=settings.openai_api_key) if settings.has_openai else None
    return ImprovementProposer(get_memory(), client=client)
