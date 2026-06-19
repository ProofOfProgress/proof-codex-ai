from shorts_bot.invideo.system_context import brief_only_for_display, load_master_context, wrap_invideo_prompt


def test_master_context_loads():
    text = load_master_context()
    assert "production soul" in text.lower() or "soul" in text.lower()
    assert "Pay" in text and "Skip" in text
    assert "9:16" in text


def test_wrap_invideo_prompt_includes_brief():
    full = wrap_invideo_prompt("Review ChatGPT Plus — Pay or Skip?")
    assert "--- VIDEO BRIEF ---" in full
    assert "Review ChatGPT Plus" in full
    assert "AI Twin" in full or "twin" in full.lower()


def test_brief_only_for_display():
    full = wrap_invideo_prompt("My product brief here")
    assert brief_only_for_display(full) == "My product brief here"
