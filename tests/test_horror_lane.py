from shorts_bot.drafts.generator import SYSTEM_PROMPT
from shorts_bot.production.ai_video_prompts import visual_dna
from shorts_bot.production.horror_lane import (
    HORROR_LANE_LABEL,
    HORROR_LANE_PRIMARY,
    analog_color_rules,
    horror_lane_compact,
)
from shorts_bot.production.world import world_rules_compact


def test_primary_lane_is_analog():
    assert HORROR_LANE_PRIMARY == "analog_horror"
    assert "Analog" in HORROR_LANE_LABEL


def test_lane_compact_rejects_creature_and_animal_cruelty():
    text = horror_lane_compact()
    assert "creature" in text.lower()
    assert "animal cruelty" in text.lower()
    assert "night-vision" in text.lower() or "night vision" in text.lower()


def test_analog_color_rules_in_visual_dna():
    rules = analog_color_rules()
    assert "night-vision" in rules.lower() or "night vision" in rules.lower()
    assert HORROR_LANE_LABEL.split()[0] in visual_dna() or "Analog" in visual_dna()


def test_world_rules_include_lane():
    assert "Analog" in world_rules_compact()
