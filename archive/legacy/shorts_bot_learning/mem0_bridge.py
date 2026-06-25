"""Mem0 long-term memory — public system adapter (falls back to SQLite-only when disabled)."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from shorts_bot.config import settings

logger = logging.getLogger(__name__)

USER_ID = "shorts_bot_channel"


def reset_mem0_cache() -> None:
    mem0_available.cache_clear()
    get_mem0.cache_clear()


@lru_cache(maxsize=1)
def mem0_available() -> bool:
    if not settings.mem0_enabled:
        return False
    if settings.has_gemini:
        return True
    if settings.has_openai:
        return True
    return False


@lru_cache(maxsize=1)
def get_mem0():
    """Lazy Mem0 client — local Qdrant under data/mem0/."""
    if not mem0_available():
        return None
    try:
        from mem0 import Memory
        from mem0.configs.base import MemoryConfig
    except ImportError:
        logger.warning("mem0ai not installed — pip install mem0ai")
        return None

    root = settings.data_dir / "mem0"
    root.mkdir(parents=True, exist_ok=True)

    if settings.has_gemini:
        key = settings.gemini_api_key
        llm_cfg = {"provider": "gemini", "config": {"model": settings.gemini_model, "api_key": key}}
        embed_cfg = {
            "provider": "gemini",
            "config": {
                "model": "models/gemini-embedding-001",
                "api_key": key,
                "embedding_dims": 768,
            },
        }
        dims = 768
    else:
        key = settings.openai_api_key
        llm_cfg = {"provider": "openai", "config": {"model": "gpt-4.1-nano-2025-04-14", "api_key": key}}
        embed_cfg = {
            "provider": "openai",
            "config": {"model": "text-embedding-3-small", "api_key": key, "embedding_dims": 1536},
        }
        dims = 1536

    cfg = MemoryConfig(
        vector_store={
            "provider": "qdrant",
            "config": {
                "path": str(root / "qdrant"),
                "collection_name": "shorts_bot_memories",
                "embedding_model_dims": dims,
            },
        },
        llm=llm_cfg,
        embedder=embed_cfg,
        history_db_path=str(root / "history.db"),
    )
    return Memory(cfg)


def remember(text: str, *, metadata: dict[str, Any] | None = None) -> bool:
    """Store a learning episode in Mem0."""
    mem = get_mem0()
    if mem is None:
        return False
    try:
        mem.add(text.strip(), user_id=USER_ID, metadata=metadata or {}, infer=False)
        return True
    except Exception as exc:
        logger.warning("Mem0 add failed: %s", exc)
        return False


def recall(query: str, *, limit: int = 5) -> list[str]:
    """Semantic search over channel learnings."""
    mem = get_mem0()
    if mem is None or not query.strip():
        return []
    try:
        result = mem.search(query.strip(), filters={"user_id": USER_ID}, limit=limit)
        rows = result.get("results") if isinstance(result, dict) else result
        if not rows:
            return []
        out: list[str] = []
        for row in rows:
            if isinstance(row, dict):
                mem_text = row.get("memory") or row.get("text") or ""
                if mem_text:
                    out.append(str(mem_text))
        return out
    except Exception as exc:
        logger.warning("Mem0 search failed: %s", exc)
        return []


def recall_context_block(query: str = "YouTube Short hooks topics workflow learnings", *, limit: int = 6) -> str:
    """Formatted block for draft / strategist prompts."""
    if not mem0_available():
        return ""
    hits = recall(query, limit=limit)
    if not hits:
        return ""
    return "MEM0 LONG-TERM MEMORY:\n" + "\n".join(f"- {h}" for h in hits)
