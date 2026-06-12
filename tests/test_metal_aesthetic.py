from shorts_bot.compliance.upload_guard import check_upload_allowed
from shorts_bot.compliance.ypp_bans import script_content_compliance_issues
from shorts_bot.config import settings
from shorts_bot.drafts.generator import SYSTEM_PROMPT
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.ai_video_prompts import negative_block, visual_dna
from shorts_bot.production.horror_lane import horror_lane_compact
from shorts_bot.production.metal_aesthetic import (
    metal_aesthetic_compact,
    script_animal_harm_issues,
    visual_prompt_animal_harm_issues,
)


def test_metal_aesthetic_in_script_prompt():
    assert "mask" in metal_aesthetic_compact().lower()
    assert "never" in metal_aesthetic_compact().lower()
    assert "mask" in SYSTEM_PROMPT.lower() or "metal" in SYSTEM_PROMPT.lower()


def test_lane_includes_metal_texture():
    text = horror_lane_compact()
    assert "industrial" in text.lower() or "metal" in text.lower()
    assert "animal cruelty" in text.lower()


def test_visual_dna_blocks_animal_harm_in_negative():
    neg = negative_block()
    assert "live bird" in neg or "animal cruelty" in neg
    assert "live bird" in visual_dna().lower() or "metal" in visual_dna().lower() or "mask" in visual_dna().lower()


def test_script_animal_harm_blocked():
    issues = script_animal_harm_issues("He was eating the bird head on stage")
    assert issues


def test_visual_prompt_animal_harm_flagged():
    issues = visual_prompt_animal_harm_issues("figure eating bird head close up gore")
    assert issues


def test_upload_guard_blocks_animal_harm_script(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ypp_safe_mode", True)
    store = MemoryStore(tmp_path / "m.db")
    mem = MemoryExtensions(store)
    script = (
        "You entered the warehouse pit alone. "
        "The mask crew stared through numbered plates. "
        "Someone was eating the bird head behind the chain curtain. "
        "You told yourself it was a prop until the crunch echoed again."
    )
    report = check_upload_allowed(
        store,
        mem,
        draft_id=9,
        topic="warehouse mask ritual",
        hook="The pit was empty except you",
        script=script,
        title="Mask segment seven",
    )
    assert not report.allowed
    assert any("animal-harm" in i.lower() or "YPP" in i for i in report.issues)


def test_script_content_compliance_export():
    assert script_content_compliance_issues("eating the bird") == script_animal_harm_issues("eating the bird")
