from shorts_bot.config import Settings
from shorts_bot.production.image_prompts import segment_to_prompt
from shorts_bot.production.turboscribe_parser import TranscriptSegment


def test_default_visual_style_is_stickfigure():
    assert Settings.model_fields["visual_style"].default == "stickfigure"


def test_stick_prompt_wording():
    prompt = segment_to_prompt(
        TranscriptSegment(0.0, "put the phone down", "00.00"),
        topic="test",
    )
    assert "stick figure" in prompt.lower()
    assert "off-white" in prompt.lower()
