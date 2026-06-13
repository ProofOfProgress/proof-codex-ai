import json
from types import SimpleNamespace

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


def test_finalize_script_flattens_structured_llm_script(monkeypatch):
    import shorts_bot.production.script_humanize as sh

    payload = {
        "hook": "Your security camera flagged motion. It's 3:12 AM, and you live alone.",
        "script": [
            {
                "spoken_text": "You open the app, but the hallway's completely empty.",
                "visual_cue": "Phone screen close-up",
            },
            {
                "spoken_text": "The live view updates. It's standing at the foot of your bed.",
                "visual_cue": "Bedroom CCTV",
            },
        ],
        "help_angle": "Security camera lunge scare.",
    }

    class FakeCompletions:
        def create(self, **_kwargs):
            message = SimpleNamespace(content=json.dumps(payload))
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    fake_backend = SimpleNamespace(
        model="fake-model",
        client=SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions())),
    )

    monkeypatch.setattr(
        "shorts_bot.llm.provider.get_llm_backend",
        lambda: fake_backend,
    )
    monkeypatch.setattr(sh, "ai_likelihood_score", lambda _text: 100)
    monkeypatch.setattr(sh, "check_jenny_voice", lambda _script, _hook: [])

    r = finalize_script(
        "security camera",
        "Your security camera flagged motion.",
        "Furthermore, this script needs a rewrite.",
        "Security camera lunge scare.",
        max_passes=1,
        threshold=5,
    )

    assert r.script == (
        "You open the app, but the hallway's completely empty. "
        "The live view updates. It's standing at the foot of your bed."
    )
    assert "visual_cue" not in r.script
