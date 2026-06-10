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
    assert "F5EFE6" in dna
    assert "bottom 40%" in dna.lower()
    assert "no faces" in dna.lower() or "Faceless" in dna


def test_templates_count_and_sunday_match():
    all_t = templates()
    assert len(all_t) == 10
    m = match_template(topic="the minute before you check your phone from the couch on Sunday")
    assert m.id == "sunday_couch_phone"


def test_segment_prompt_includes_framework_parts():
    seg = TranscriptSegment(0.0, "Your thumb hovers over the lock screen.", "00.00")
    topic = "Sunday phone check from the couch"
    prompt = segment_to_video_prompt(seg, topic=topic)
    assert "SUBJECT:" in prompt
    assert "ACTION:" in prompt
    assert "CAMERA:" in prompt
    assert "ENVIRONMENT:" in prompt
    assert "END STATE:" in prompt
    assert visual_dna()[:40] in prompt


def test_continuity_chain_links_clips():
    segs = [
        TranscriptSegment(0.0, "On the couch.", "00.00"),
        TranscriptSegment(4.0, "Three breaths.", "00.04"),
    ]
    briefs = build_video_prompt_briefs(segs, topic="couch sunday phone", total_duration=10.0)
    assert len(briefs) == 2
    assert "CONTINUITY IN:" in briefs[1].prompt
    assert briefs[0].end_state in briefs[1].prompt


def test_negative_block_bans_text_and_faces():
    neg = negative_block()
    assert "no text" in neg
    assert "no faces" in neg


def test_match_template_falls_back_to_derived():
    m = match_template(topic="something completely unrelated xyz", spoken_text="abstract notion")
    assert m.id == "derived"
