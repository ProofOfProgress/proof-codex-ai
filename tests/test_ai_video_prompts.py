from shorts_bot.production.ai_video_prompts import (
    build_video_prompt_briefs,
    match_template,
    negative_block,
    segment_to_video_prompt,
    templates,
    visual_dna,
)
from shorts_bot.production.turboscribe_parser import TranscriptSegment


def test_visual_dna_has_palette_and_safe_zone():
    dna = visual_dna()
    assert "0A0A0A" in dna
    assert "bottom 40%" in dna.lower()
    assert "horror" in dna.lower()


def test_templates_count_and_mirror_match():
    all_t = templates()
    assert len(all_t) == 10
    m = match_template(topic="the mirror reflection blinked after you did")
    assert m.id == "mirror_blink"


def test_segment_prompt_includes_framework_parts():
    seg = TranscriptSegment(0.0, "Your reflection blinked one second late.", "00.00")
    topic = "mirror blink wrong reflection"
    prompt = segment_to_video_prompt(seg, topic=topic)
    assert "SUBJECT:" in prompt
    assert "ACTION:" in prompt
    assert "CAMERA:" in prompt
    assert "ENVIRONMENT:" in prompt
    assert "END STATE:" in prompt
    assert visual_dna()[:40] in prompt


def test_continuity_chain_links_clips():
    segs = [
        TranscriptSegment(0.0, "Motion flagged on security cam.", "00.00"),
        TranscriptSegment(4.0, "You told yourself it was nothing.", "00.04"),
    ]
    briefs = build_video_prompt_briefs(segs, topic="security cam alone", total_duration=10.0)
    assert len(briefs) == 2
    assert "CONTINUITY IN:" in briefs[1].prompt
    assert briefs[0].end_state in briefs[1].prompt


def test_negative_block_bans_cosy_and_text():
    neg = negative_block()
    assert "no text" in neg
    assert "cosy" in neg
    assert "stick figures" in neg


def test_match_template_falls_back_to_derived():
    m = match_template(topic="something completely unrelated xyz", spoken_text="abstract notion")
    assert m.id == "derived_horror"


def test_final_segment_uses_jumpscare_template():
    segs = [
        TranscriptSegment(0.0, "You heard a knock.", "00.00"),
        TranscriptSegment(5.0, "You turned — it opened its mouth.", "00.05"),
    ]
    briefs = build_video_prompt_briefs(segs, topic="knock closet", total_duration=12.0)
    assert briefs[-1].template_id == "jumpscare_lunge"
