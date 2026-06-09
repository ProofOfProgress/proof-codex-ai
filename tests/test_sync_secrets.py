import os
from pathlib import Path

from scripts.sync_secrets import sync


def test_sync_openai_key_to_env(tmp_path: Path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=sk-your-key-here\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-real-key-abc123")
    monkeypatch.chdir(tmp_path)

    # Point sync at tmp .env by patching module path
    import scripts.sync_secrets as mod

    monkeypatch.setattr(mod, "ENV_PATH", env_file)
    monkeypatch.setattr(mod, "ROOT", tmp_path)

    written = sync(quiet=True)
    assert "OPENAI_API_KEY" in written
    content = env_file.read_text(encoding="utf-8")
    assert "sk-test-real-key-abc123" in content
    assert "your-key" not in content


def test_sync_skips_placeholder(monkeypatch, tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=sk-old\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-your-key-here")
    monkeypatch.chdir(tmp_path)

    import scripts.sync_secrets as mod

    monkeypatch.setattr(mod, "ENV_PATH", env_file)
    monkeypatch.setattr(mod, "ROOT", tmp_path)

    written = sync(quiet=True)
    assert written == []
    assert env_file.read_text(encoding="utf-8") == "OPENAI_API_KEY=sk-old\n"
