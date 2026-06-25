"""Tests for Mem0 bridge (mocked — no API in CI)."""

from unittest.mock import MagicMock, patch

from shorts_bot.learning import mem0_bridge


def test_recall_context_block_with_mock(monkeypatch):
    monkeypatch.setattr(mem0_bridge, "mem0_available", lambda: True)
    fake = MagicMock()
    fake.search.return_value = {"results": [{"memory": "Hook X worked on Claude Pro"}]}
    monkeypatch.setattr(mem0_bridge, "get_mem0", lambda: fake)
    block = mem0_bridge.recall_context_block()
    assert "MEM0" in block
    assert "Hook X" in block
