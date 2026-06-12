from pathlib import Path

from shorts_bot.codex.chunks import chunk_markdown
from shorts_bot.codex.index import CodexIndex
from shorts_bot.codex.search import CodexSearcher, tokenize


def test_tokenize_lowercase():
    assert "suspense" in tokenize("How do I build SUSPENSE in horror?")


def test_chunk_markdown_splits_sections(tmp_path: Path):
    md = tmp_path / "sample.md"
    md.write_text(
        "# Title\n\nIntro paragraph here with enough text to pass minimum.\n\n"
        "## Hooks\n\nHook advice for retention and suspense in shorts.\n\n"
        "## Payoff\n\nFinale scare and jumpscare timing notes here.\n",
        encoding="utf-8",
    )
    chunks = chunk_markdown(md, layer="docs", workspace=tmp_path.parent)
    assert len(chunks) >= 2
    assert any("Hooks" in c.section for c in chunks)


def test_search_ranks_relevant_chunk(tmp_path: Path):
    md = tmp_path / "horror.md"
    md.write_text(
        "## Suspense\n\n"
        "Build suspense with impossible details, slow VO, and delayed payoff.\n\n"
        "## Comedy\n\n"
        "Do not use comedy beats in Peripheral horror shorts.\n",
        encoding="utf-8",
    )
    chunks = chunk_markdown(md, layer="research", workspace=tmp_path.parent)
    searcher = CodexSearcher(chunks)
    hits = searcher.search("how to build suspense horror short")
    assert hits
    assert "suspense" in hits[0].chunk.text.lower()


def test_codex_index_builds_from_repo():
    idx = CodexIndex.build(force=True)
    assert len(idx.chunks) > 20
    sources = idx.list_sources()
    paths = {str(s["path"]) for s in sources}
    assert any(p.startswith("course/files/") for p in paths)
    assert any(p.startswith("data/research/") for p in paths)


def test_parse_codex_request():
    from shorts_bot.services.chat_router import parse_codex_request

    assert parse_codex_request("codex ask how build suspense") == (
        "ask",
        "how build suspense",
    )
    assert parse_codex_request("codex search retention hook") == (
        "search",
        "retention hook",
    )
    assert parse_codex_request("draft mirror horror") is None


def test_ask_codex_search_only():
    from shorts_bot.codex.ask import ask_codex

    result = ask_codex("suspense retention horror short", search_only=True)
    assert result.mode == "search-only"
    assert result.sources or "No Codex" in result.answer
