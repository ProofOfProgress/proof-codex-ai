"""Caption line wrap — 20 chars per line owner rule (safe TikTok margin)."""

from shorts_bot.tiktok_shop.captions import (
    on_screen_caption,
    product_phrase,
    validate_hook_lines,
    wrap_hook_lines,
)


def test_product_phrase_default_this():
    assert product_phrase("Insulated Tumbler") == "this insulated tumbler"
    assert product_phrase("Car Phone Mount") == "this car phone mount"


def test_product_phrase_custom_determiner():
    assert product_phrase("Egg Cooker", determiner="an") == "an egg cooker"
    assert product_phrase("Car Phone Mount", determiner="a") == "a car phone mount"


def test_on_screen_caption_uses_spoken_phrase():
    cap = on_screen_caption("Insulated Tumbler")
    assert "this insulated tumbler" in cap
    assert "Insulated Tumbler" not in cap


def test_wrap_hook_lines_max_20():
    lines = wrap_hook_lines(on_screen_caption("Insulated Tumbler"))
    assert lines
    assert all(len(ln) <= 20 for ln in lines)
    assert validate_hook_lines(lines) == []


def test_wrap_long_word_splits():
    lines = wrap_hook_lines("hello supercalifragilisticexpialidocious world", max_chars_per_line=20)
    assert all(len(ln) <= 20 for ln in lines)


def test_wrap_on_screen_caption_compat():
    from shorts_bot.tiktok_shop.video_editor import wrap_on_screen_caption

    wrapped = wrap_on_screen_caption(on_screen_caption("Test Product"))
    for line in wrapped.splitlines():
        assert len(line) <= 20
