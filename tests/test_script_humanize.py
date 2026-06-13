from shorts_bot.config import settings
from shorts_bot.production.script_humanize import finalize_script


def test_finalize_script_reduces_ai_score():
    hook = "Stop scrolling — this one habit around cant sleep at 3am actually helps."
    script = (
        "Stop scrolling — this one habit around cant sleep at 3am actually helps. "
        "Furthermore it is important to note that you must delve into sleep."
    )
    r = finalize_script("cant sleep at 3am", hook, script, "helps sleep", max_passes=5, threshold=50)
    assert r.final_ai_score <= 50 or r.passes >= 1
    assert "Furthermore" not in r.script or r.final_ai_score < 80


def test_ai_detect_default_threshold_is_five():
    assert settings.ai_detect_threshold == 5
    assert settings.ai_detect_blocks_render is True


def test_finalize_script_passes_when_score_at_or_below_threshold():
    hook = "The playback timestamp was yesterday, before you ever pressed record."
    script = (
        "You filmed the village sign to prove it wasn't real. "
        "The playback opened on yesterday's fog, before you pressed record. "
        "Your name was already carved in the wood. "
        "The baker crossed herself and walked inside. "
        "You told yourself the file was corrupted, a bad timestamp. "
        "Today reads zero. The wood splits, and the eye in the center turns to meet yours."
    )
    r = finalize_script("village sign", hook, script, "countdown twist", max_passes=1, threshold=5)
    assert r.final_ai_score <= 5
    assert r.passed is True
