from pathlib import Path

from shorts_bot.memory.agent_memory import (
    AgentMemoryStore,
    is_memory_list_request,
    parse_forget_request,
    parse_remember_request,
)
from shorts_bot.memory.store import MemoryStore
from shorts_bot.services.ops import BotOperations


def test_agent_memory_crud(tmp_path: Path):
    store = MemoryStore(tmp_path / "mem.db")
    mem_store = AgentMemoryStore(store)
    mem = mem_store.add_memory(content="Always use ffmpeg captions", category="operating_rule")
    assert mem.id >= 1
    listed = mem_store.list_memories()
    assert any(m.id == mem.id for m in listed)
    assert mem_store.delete_memory(mem.id)
    assert not mem_store.delete_memory(999)


def test_context_block_includes_saved_memory(tmp_path: Path):
    store = MemoryStore(tmp_path / "mem2.db")
    mem_store = AgentMemoryStore(store)
    mem_store.add_memory(content="Niche is Don't Blink", category="operating_rule", pinned=True)
    block = mem_store.context_block()
    assert "LONG-TERM MEMORY" in block
    assert "Don't Blink" in block


def test_export_markdown(tmp_path: Path):
    store = MemoryStore(tmp_path / "mem3.db")
    mem_store = AgentMemoryStore(store)
    mem_store.add_memory(content="Test fact for export", category="fact")
    out = tmp_path / "MEMORY.md"
    path = mem_store.export_markdown(out)
    text = path.read_text(encoding="utf-8")
    assert "Agent memory" in text
    assert "Test fact for export" in text


def test_remember_and_forget_parsers():
    assert parse_remember_request("remember: use API not browser") == ("fact", "use API not browser")
    assert parse_remember_request("operating rule: never ask clarifying questions") == (
        "operating_rule",
        "never ask clarifying questions",
    )
    assert parse_forget_request("forget 12") == 12
    assert parse_forget_request("forget #3") == 3
    assert is_memory_list_request("memory")
    assert is_memory_list_request("operating rules")


def test_ops_remember_flow(tmp_path: Path, monkeypatch):
    from shorts_bot import config

    monkeypatch.setattr(config.settings, "database_path", tmp_path / "ops_mem.db")
    monkeypatch.setattr(config.settings, "memory_markdown_path", tmp_path / "MEMORY.md")

    import shorts_bot.web.deps as deps

    deps._store = None
    deps._agent_memory = None
    deps._agent = None

    ops = BotOperations()
    saved = ops.remember_agent_memory("Prefer web UI for pipeline control", category="preference")
    assert "Saved memory" in saved
    listed = ops.list_agent_memory()
    assert "web UI" in listed
    forget_id = int(saved.split("#")[1].split()[0])
    forgot = ops.forget_agent_memory(forget_id)
    assert "Forgot" in forgot
