from shorts_bot.drafts.generator import SYSTEM_PROMPT
from shorts_bot.production.ai_video_prompts import visual_dna
from shorts_bot.production.visual_identity import face_eye_visibility_rules


def test_face_eye_rules_not_silhouettes_only():
    rules = face_eye_visibility_rules().lower()
    assert "not saved for finale only" in rules or "not finale-only" in rules
    assert "silhouettes only" not in rules


def test_visual_dna_allows_early_eyes_and_masks():
    dna = visual_dna().lower()
    assert "silhouettes only" not in dna
    assert "identifiable faces until final" not in dna
    assert "macro" in dna or "eye" in dna
    assert "mask" in dna


def test_generator_prompt_allows_visible_eyes():
    prompt = SYSTEM_PROMPT.lower()
    assert "faceless" not in prompt or "not saved for finale" in prompt
    assert "macro" in prompt or "eye" in prompt
    assert "silhouettes only" not in prompt
