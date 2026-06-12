from shorts_bot.production.black_mirror_format import (
    black_mirror_format_compact,
    black_mirror_format_doc_path,
    black_mirror_script_structure,
)


def test_black_mirror_doc_exists():
    assert black_mirror_format_doc_path().exists()


def test_black_mirror_format_compact():
    text = black_mirror_format_compact()
    assert "Black Mirror" in text
    assert "twist" in text.lower()
    assert "premise" in text.lower()


def test_black_mirror_script_structure():
    text = black_mirror_script_structure()
    assert "TWIST" in text
    assert "STING" in text
