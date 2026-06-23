from shorts_bot.invideo.ms_byte import ms_byte_brief
from shorts_bot.invideo.prompts import DEFAULT_CHATGPT_PLUS_BRIEF, shorts_product_brief


def test_shorts_brief_includes_vertical_rules():
    brief = shorts_product_brief(product="Notion AI", hook="Is it worth it?")
    assert "9:16" in brief
    assert "NOT long-form" in brief or "YouTube Short ONLY" in brief
    assert "Notion AI" in brief
    assert "strength" in brief.lower() or "STRENGTH" in brief


def test_default_chatgpt_brief():
    assert "ChatGPT Plus" in DEFAULT_CHATGPT_PLUS_BRIEF
    assert "vertical" in DEFAULT_CHATGPT_PLUS_BRIEF.lower() or "9:16" in DEFAULT_CHATGPT_PLUS_BRIEF


def test_ms_byte_brief_jenny_and_tts():
    brief = ms_byte_brief(
        product="Grok",
        hook="Thirty bucks for Grok — most shouldn't pay.",
        strength_hint="Live Twitter data",
        weakness_hint="$30 vs $20 rivals",
    )
    assert "JENNY" in brief or "HOOK" in brief
    assert "Twitter" in brief or "NEVER say" in brief
    assert "Pay / Skip / Wait" in brief or "NO Pay" in brief
    assert "RTR_MsByte" in brief
    assert "45" in brief  # rich host screen time
