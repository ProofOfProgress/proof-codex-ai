"""Peripheral shared universe — The Gap analog apartment horror."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.black_mirror_format import (
    black_mirror_format_compact,
    black_mirror_script_structure,
)
from shorts_bot.production.horror_lane import HORROR_LANE_LABEL, horror_lane_compact

WORLD_NAME = "The Gap"
WORLD_TAGLINE = "Recordings lag behind reality — the Eye still watches from the old village lore."

_WORLD_DOC = Path("channel/brand/world.md")


def world_doc_path() -> Path:
    return _WORLD_DOC


def world_rules_compact() -> str:
    """Short rules block for prompts (scripts + agents)."""
    return f"""UNIVERSE — Peripheral (~30s nightmare Shorts):
{WORLD_TAGLINE}
{black_mirror_format_compact()}
Laws: second-person ownership hooks; no soft narrator; recordings can show what reality hides; old village worship of the Eye leaks through mirrors, masks, and dreams.
Twist rewrites hook; finale sting on NEW truth — then stop.
Settings: Analog fullscreen CCTV apartment (primary) — hall, door, mirror, nightstand alarm clock, REC HUD, 3:12 AM. The fog village and Eye worship remain background lore, not the default set.
Threat: the lag — feed sees motion first; Eye/mask/reflection appears one beat late; final jumpscare proves the room was never empty.
Not this world: phone screens, generic creature chase, comfort/self-help visuals, unearned glitch-hour spam.
{horror_lane_compact()}"""


def world_lore_for_scripts() -> str:
    """Script writer context — structure + world laws."""
    return f"""{world_rules_compact()}

{black_mirror_script_structure()}

Write each Short as second-person owned horror where possible: "Your security camera..." / "You hear..."
Use first-person only when the story needs character dialogue.
Dream/Eye/village Shorts are allowed as lore variants; default to analog CCTV and a clear jumpscare payoff."""


def world_visual_continuity() -> str:
    """Paste into every video / image prompt after visual DNA."""
    return (
        "WORLD — Peripheral / The Gap: fullscreen CCTV apartment, empty hallway, door, mirror, "
        "nightstand alarm clock at 3:12 AM, REC HUD, night-vision green, VHS grain; "
        "old fog village / Eye worship motifs can leak into reflections or dreams; "
        "cinematic horror — no smartphones, no phone UI, no comfort/self-help visuals."
    )


def world_motifs() -> tuple[str, ...]:
    """Recurring in-universe tokens for topic/QC checks."""
    return (
        "eye",
        "the eye",
        "analog",
        "cctv",
        "security camera",
        "motion",
        "3:12",
        "the gap",
        "apartment",
        "recording",
        "village",
        "villager",
        "worship",
        "ritual",
        "dream",
        "remembered",
        "sign",
        "signpost",
        "barn",
        "fog",
        "candle",
        "omen",
        "curse",
        "uncanny",
        "premise",
        "twist",
        "don't blink",
        "peripheral",
    )


def world_summary_for_brand() -> str:
    """Loaded by ChannelBrand when world.md exists."""
    if _WORLD_DOC.exists():
        text = _WORLD_DOC.read_text(encoding="utf-8").strip()
        return text[:1200]
    return world_rules_compact()
