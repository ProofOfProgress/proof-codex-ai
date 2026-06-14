from shorts_bot.production.blender.gemini_blender_reference import (
    LIGHTS_ARE_OFF_URLS,
    gemini_blender_quality_prompt,
    reference_links_block,
)


def test_reference_links_include_owner_urls():
    block = reference_links_block()
    for url in LIGHTS_ARE_OFF_URLS:
        assert url in block


def test_gemini_blender_quality_prompt_includes_scene():
    prompt = gemini_blender_quality_prompt(scene="Draft #2 gas station")
    assert "Draft #2 gas station" in prompt
    assert LIGHTS_ARE_OFF_URLS[0] in prompt
    assert "LIGHTS ARE OFF" in prompt
