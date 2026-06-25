from shorts_bot.production.framing import (
    CAPTION_BOTTOM_MARGIN_PX,
    FRAME_HEIGHT,
    caption_bar_y,
)


def test_caption_bar_above_shorts_ui_overlay():
    bar_h = 100
    y = caption_bar_y(bar_h, frame_height=FRAME_HEIGHT)
    bottom_edge = y + bar_h
    assert bottom_edge <= FRAME_HEIGHT - CAPTION_BOTTOM_MARGIN_PX
    assert y < FRAME_HEIGHT - 400  # well above old 80px margin


def test_framing_notes_mention_jenny_safe_zone():
    from shorts_bot.production.framing import framing_notes_for_prompt

    notes = framing_notes_for_prompt()
    assert "15% and 55%" in notes
    assert "caption" in notes.lower() and "safe zone" in notes.lower()
