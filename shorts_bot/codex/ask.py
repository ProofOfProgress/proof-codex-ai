"""Ask Codex — search + Gemini answer with citations."""

from __future__ import annotations

from dataclasses import dataclass, field

from shorts_bot.codex import CODEX_NAME
from shorts_bot.codex.index import CodexIndex
from shorts_bot.codex.search import SearchHit
from shorts_bot.config import settings
from shorts_bot.course.loader import CourseKnowledgeBase
from shorts_bot.course.router import CourseRouter


@dataclass
class CodexAskResult:
    question: str
    answer: str
    sources: list[dict[str, str | float]] = field(default_factory=list)
    router_lever: str = ""
    router_files: list[str] = field(default_factory=list)
    mode: str = "ask"  # ask | search-only
    message: str = ""


def _format_context(hits: list[SearchHit], *, max_chars: int) -> str:
    blocks: list[str] = []
    used = 0
    for i, hit in enumerate(hits, start=1):
        header = f"[{i}] {hit.chunk.citation} (layer: {hit.chunk.layer}, score: {hit.score:.2f})"
        body = hit.chunk.text.strip()
        block = f"{header}\n{body}"
        if used + len(block) > max_chars:
            break
        blocks.append(block)
        used += len(block)
    return "\n\n---\n\n".join(blocks)


def search_codex(
    query: str,
    *,
    limit: int | None = None,
    index: CodexIndex | None = None,
) -> list[SearchHit]:
    idx = index or CodexIndex.build()
    lim = limit or settings.codex_search_max_chunks
    return idx.searcher.search(query, limit=lim)


def ask_codex(
    question: str,
    *,
    search_only: bool = False,
    index: CodexIndex | None = None,
) -> CodexAskResult:
    """Retrieve relevant Codex chunks; optionally answer with Gemini."""
    idx = index or CodexIndex.build()
    hits = search_codex(question, index=idx)

    kb = CourseKnowledgeBase(settings.course_dir)
    router = CourseRouter(kb)
    route = router.route(question)

    sources = [
        {
            "path": h.chunk.source_path,
            "section": h.chunk.section,
            "layer": h.chunk.layer,
            "score": round(h.score, 3),
            "citation": h.chunk.citation,
        }
        for h in hits
    ]

    if not hits:
        return CodexAskResult(
            question=question,
            answer=(
                "No Codex passages matched that query. Try broader words "
                "(e.g. suspense, retention, hook, jumpscare) or run "
                "`python3 -m shorts_bot.codex list` to browse sources."
            ),
            sources=[],
            router_lever=route.main_lever,
            router_files=route.files,
            mode="search-only",
            message="No hits",
        )

    context = _format_context(hits, max_chars=settings.codex_max_context_chars)
    router_snippet = router.build_guidance(question)[:2500]

    if search_only or not settings.has_full_chat:
        lines = [f"**Codex search** — {len(hits)} hit(s) for: {question}\n"]
        for h in hits:
            preview = h.chunk.text[:280].replace("\n", " ")
            lines.append(f"- [{h.score:.2f}] {h.chunk.citation}\n  {preview}…")
        lines.append(f"\nRouter lever: {route.main_lever} (files {', '.join(route.files)})")
        return CodexAskResult(
            question=question,
            answer="\n".join(lines),
            sources=sources,
            router_lever=route.main_lever,
            router_files=route.files,
            mode="search-only",
            message="Search-only (no LLM or search_only=True)",
        )

    from shorts_bot.llm.provider import get_llm_backend

    backend = get_llm_backend()
    if backend is None:
        return ask_codex(question, search_only=True, index=idx)

    system = f"""You are the Peripheral / Shorts Bot strategist answering from **{CODEX_NAME}** only.

Rules:
- Answer ONLY from the RETRIEVED PASSAGES and ROUTER CONTEXT below — no outside creator folklore.
- Cite sources as [1], [2] matching passage numbers.
- Plain English; actionable steps for horror Shorts production.
- If passages are thin, say what is missing and point to the best file path to read manually.
- Channel: Peripheral (faceless horror Shorts, ~30s, jumpscare payoff)."""

    user = f"""QUESTION:
{question}

ROUTER (Jenny lever: {route.main_lever}, files {', '.join(route.files)}):
{router_snippet}

RETRIEVED PASSAGES:
{context}

Answer in 3 parts:
1. Direct answer (2–5 bullets)
2. How to apply on the next Peripheral Short
3. Sources used [n] — list paths"""

    response = backend.client.chat.completions.create(
        model=backend.model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.4,
    )
    answer = (response.choices[0].message.content or "").strip()

    return CodexAskResult(
        question=question,
        answer=answer,
        sources=sources,
        router_lever=route.main_lever,
        router_files=route.files,
        mode="ask",
        message=f"Answered via {backend.provider}",
    )
