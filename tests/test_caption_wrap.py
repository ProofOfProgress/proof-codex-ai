"""Caption line wrap — 18 chars per line owner rule (safe TikTok margin)."""

from shorts_bot.tiktok_shop.captions import (
    on_screen_caption,
    validate_hook_lines,
    wrap_hook_lines,
)


def test_wrap_hook_lines_max_18():
    lines = wrap_hook_lines(on_screen_caption("Insulated Tumbler"))
    assert lines
    assert all(len(ln) <= 18 for ln in lines)
    assert validate_hook_lines(lines) == []


def test_wrap_long_word_splits():
    lines = wrap_hook_lines("hello supercalifragilisticexpialidocious world", max_chars_per_line=18)
    assert all(len(ln) <= 18 for ln in lines)


def test_wrap_on_screen_caption_compat():
    from shorts_bot.tiktok_shop.video_editor import wrap_on_screen_caption

    wrapped = wrap_on_screen_caption(on_screen_caption("Test Product"))
    for line in wrapped.splitlines():
        assert len(line) <= 18
