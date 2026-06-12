from shorts_bot.codex.context import (
    codex_context_for_agent,
    should_query_codex,
)


def test_should_query_codex_strategy_questions():
    assert should_query_codex("how can I build suspense in my horror short?")
    assert should_query_codex("best hook for retention")
    assert not should_query_codex("sync youtube")
    assert not should_query_codex("approve 3")
    assert not should_query_codex("dev: fix the web ui")


def test_codex_context_for_agent_returns_search_block():
    block, mode = codex_context_for_agent("how to build suspense horror short")
    assert mode == "search"
    assert "CODEX RETRIEVAL" in block
    assert "Router lever" in block or "No Codex" in block


def test_codex_context_skips_ops():
    block, mode = codex_context_for_agent("sync analytics")
    assert mode == "skip"
    assert block == ""
