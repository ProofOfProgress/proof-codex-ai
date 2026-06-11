from shorts_bot.config import Settings
from shorts_bot.production.image_prompts import segment_to_prompt
from shorts_bot.production.turboscribe_parser import TranscriptSegment


def test_default_visual_style_is_ai_video():
    assert Settings.model_fields["visual_style"].default == "ai_video"


def test_ai_video_uses_paid_still_prompts():
    from shorts_bot.config import settings

    seg = TranscriptSegment(0.0, "phone on nightstand", "00.00")
    if settings.visual_style in ("ai", "ai_video", "hybrid", "ai_video_hook"):
        from shorts_bot.production.image_prompts import ai_segment_to_prompt

        prompt = ai_segment_to_prompt(seg, topic="test")
        assert "vertical 9:16" in prompt.lower()
    else:
        prompt = segment_to_prompt(seg, topic="test")
        assert "stick figure" in prompt.lower()


def test_stick_prompt_wording():
    prompt = segment_to_prompt(
        TranscriptSegment(0.0, "put the phone down", "00.00"),
        topic="test",
    )
    assert "stick figure" in prompt.lower()
    assert "warm cream" in prompt.lower() or "cosy" in prompt.lower()
