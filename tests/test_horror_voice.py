from shorts_bot.production.tts.horror_voice import (
    DEFAULT_RESEMBLE_PROMPT,
    edge_horror_prosody,
    prepare_horror_resemble_ssml,
)


SAMPLE = (
    "You blinked at the mirror. Your reflection blinked one second later. "
    "You told yourself it was just tired eyes. Then it lunged."
)


def test_resemble_ssml_has_horror_prompt_and_breaks():
    ssml = prepare_horror_resemble_ssml(SAMPLE)
    assert ssml.startswith("<speak")
    assert "prompt=" in ssml
    assert DEFAULT_RESEMBLE_PROMPT[:20] in ssml
    assert "<break" in ssml
    assert "lunged" in ssml


def test_edge_prosody_slows_false_calm_speeds_finale():
    sentences = SAMPLE.replace(".", "|").split("|")
    sentences = [s.strip() for s in sentences if s.strip()]
    calm_rate, _ = edge_horror_prosody(sentences[2], index=2, total=4)
    finale_rate, _ = edge_horror_prosody(sentences[3], index=3, total=4)
    assert int(calm_rate.replace("%", "")) < int(finale_rate.replace("%", ""))
