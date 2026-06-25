from pathlib import Path

from shorts_bot.codex import CODEX_NAME, CODEX_BLURB, load_codex


def test_codex_name():
    assert CODEX_NAME == "Codex"
    assert "Codex" in CODEX_BLURB


def test_load_codex_reads_nine_files():
    kb = load_codex(Path("course"))
    assert len(kb.all_files()) == 9
