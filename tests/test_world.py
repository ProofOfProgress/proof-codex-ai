from shorts_bot.brand.loader import ChannelBrand
from shorts_bot.drafts.generator import SYSTEM_PROMPT
from shorts_bot.production.ai_video_prompts import visual_dna
from shorts_bot.production.image_prompts import horror_segment_to_prompt
from shorts_bot.production.niche import NICHE_POSITIONING
from shorts_bot.production.turboscribe_parser import TranscriptSegment
from shorts_bot.production.world import (
    WORLD_NAME,
    world_doc_path,
    world_lore_for_scripts,
    world_motifs,
    world_rules_compact,
    world_visual_continuity,
)


def test_world_doc_exists():
    assert world_doc_path().exists()


def test_world_rules_compact_mentions_village_and_eye():
    rules = world_rules_compact()
    assert "village" in rules.lower()
    assert "Eye" in rules
    assert "worship" in rules.lower()
    assert "twist" in rules.lower()


def test_world_visual_continuity_in_i2v_dna():
    dna = visual_dna()
    assert "Peripheral" in dna
    assert world_visual_continuity() in dna


def test_niche_positioning_includes_world():
    assert WORLD_NAME in NICHE_POSITIONING
    assert "worship" in NICHE_POSITIONING.lower()


def test_generator_system_prompt_includes_world():
    assert "Eye" in SYSTEM_PROMPT
    assert "worship" in SYSTEM_PROMPT.lower()
    assert world_lore_for_scripts()[:40] in SYSTEM_PROMPT


def test_image_prompt_includes_world():
    seg = TranscriptSegment(0.0, "I saw them praying to the Eye.", "00.00")
    prompt = horror_segment_to_prompt(seg, topic="village worship")
    assert "Peripheral" in prompt or WORLD_NAME in prompt


def test_brand_loader_includes_world_bible():
    brand = ChannelBrand()
    instructions = brand.draft_instructions()
    assert "WORLD BIBLE" in instructions
    assert "Eye" in instructions or WORLD_NAME in instructions


def test_world_motifs_non_empty():
    motifs = world_motifs()
    assert "eye" in motifs
    assert "village" in motifs
