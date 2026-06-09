from shorts_bot.production.voiceover import _clean_script_for_tts, list_voices


def test_clean_script_strips_hook_header():
    raw = "HOOK: Hello\n\nSay this calmly.\n\n---\nRecord this.\n"
    assert _clean_script_for_tts(raw) == "Say this calmly. Record this."


def test_list_voices_nonempty():
    assert "en-US-AriaNeural" in list_voices()
