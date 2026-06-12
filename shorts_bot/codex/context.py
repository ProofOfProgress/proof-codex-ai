"""Codex context blocks for agents — search-first, optional full ask."""

from __future__ import annotations

import re

from shorts_bot.codex.ask import ask_codex, search_codex
from shorts_bot.config import settings
from shorts_bot.course.loader import CourseKnowledgeBase
from shorts_bot.course.router import CourseRouter


# Strategy / craft questions → retrieve Codex before answering.
_CODEX_TRIGGER_RE = re.compile(
    r"\b("
    r"how\s+(?:do|can|should|to)|"
    r"what\s+(?:is|are|makes)|"
    r"why\s+(?:do|does|is)|"
    r"when\s+(?:should|to)|"
    r"best\s+(?:way|practice)|"
    r"suspense|retention|hook|payoff|pacing|jumpscare|"
    r"script|visual|editing|cta|analytics|"
    r"horror|scare|tension|dread|"
    r"codex|course|jenny|lever"
    r")\b",
    re.I,
)


def should_query_codex(message: str) -> bool:
    """True when the message is a craft/strategy question Codex can answer."""
    text = (message or "").strip()
    if not text:
        return False
    lower = text.lower()
    if lower.startswith(("codex ", "ask codex", "course ")):
        return True
    # Skip pure ops commands
    ops_prefixes = (
        "draft ",
        "approve ",
        "reject ",
        "sync",
        "finish ",
        "make video",
        "dev:",
        "build:",
        "pending",
        "upload ",
        "render ",
    )
    if any(lower.startswith(p) for p in ops_prefixes):
        return False
    return bool(_CODEX_TRIGGER_RE.search(text))


def format_search_hits(question: str, *, limit: int | None = None) -> str:
    """BM25 passages + router lever — no extra LLM call."""
    hits = search_codex(question, limit=limit or settings.codex_search_max_chunks)
    if not hits:
        return "No Codex passages matched. Try broader keywords or `python3 -m shorts_bot.codex list`."

    kb = CourseKnowledgeBase(settings.course_dir)
    route = CourseRouter(kb).route(question)
    lines = [
        f"Router lever: {route.main_lever} (files {', '.join(route.files)})",
        "",
    ]
    max_chars = settings.codex_max_context_chars
    used = 0
    for i, hit in enumerate(hits, start=1):
        block = (
            f"[{i}] {hit.chunk.citation} (score {hit.score:.2f}, layer {hit.chunk.layer})\n"
            f"{hit.chunk.text.strip()}"
        )
        if used + len(block) > max_chars:
            break
        lines.append(block)
        lines.append("")
        used += len(block)
    return "\n".join(lines).strip()


def codex_context_for_agent(
    question: str,
    *,
    full_ask: bool = False,
) -> tuple[str, str]:
    """
    Return (context_block, mode) for injection into agent prompts.
    mode: search | ask | skip
    """
    if not should_query_codex(question):
        return "", "skip"

    if full_ask and settings.has_full_chat:
        result = ask_codex(question, search_only=False)
        block = (
            f"CODEX ANSWER ({result.mode}):\n{result.answer}\n\n"
            f"Sources: {', '.join(s['path'] for s in result.sources[:5])}"
        )
        return block[: settings.codex_max_context_chars], "ask"

    block = format_search_hits(question)
    return f"CODEX RETRIEVAL (search only — cite paths):\n{block}", "search"
