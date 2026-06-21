import pytest

from shorts_bot.config import Settings
from shorts_bot.production.image_prompts import horror_segment_to_prompt
from shorts_bot.production.turboscribe_parser import TranscriptSegment


def test_default_visual_style_is_ai_video():
    assert Settings.model_fields["visual_style"].default == "ai_video"


@pytest.mark.skip(reason="Legacy horror image prompts deprecated — InVideo pivot")
def test_horror_prompt_wording():
    prompt = horror_segment_to_prompt(
        TranscriptSegment(0.0, "the mirror blinked after you did", "00.00"),
        topic="wrong reflection",
    )
    assert "horror" in prompt.lower()
    assert "vertical 9:16" in prompt.lower()
    assert "stick" not in prompt.lower()
    assert "cosy" not in prompt.lower()
    assert "cream" not in prompt.lower()
