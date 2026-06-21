from shorts_bot.invideo.prompts import DEFAULT_CHATGPT_PLUS_BRIEF, shorts_product_brief


def test_shorts_brief_includes_vertical_rules():
    brief = shorts_product_brief(product="Notion AI", hook="Is it worth it?")
    assert "9:16" in brief
    assert "NOT long-form" in brief
    assert "Notion AI" in brief


def test_default_chatgpt_brief():
    assert "ChatGPT Plus" in DEFAULT_CHATGPT_PLUS_BRIEF
    assert "vertical" in DEFAULT_CHATGPT_PLUS_BRIEF.lower()
