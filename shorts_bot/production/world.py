"""Peripheral shared universe — The Gap surveillance horror."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.black_mirror_format import (
    black_mirror_format_compact,
    black_mirror_script_structure,
)
from shorts_bot.production.horror_lane import HORROR_LANE_LABEL, horror_lane_compact

WORLD_NAME = "The Gap"
WORLD_TAGLINE = "Reality lags behind the recording at 3:12 AM."

_WORLD_DOC = Path("channel/brand/world.md")


def world_doc_path() -> Path:
    return _WORLD_DOC


def world_rules_compact() -> str:
    """Short rules block for prompts (scripts + agents)."""
    return f"""UNIVERSE — Peripheral (~30s analog horror Shorts):
{WORLD_TAGLINE}
{black_mirror_format_compact()}
Laws: first-person or camera-owned POV; character voices on screen only (no narrator); cameras, mirrors, and alarm clocks reveal the lag before the room does.
Twist rewrites hook; finale sting on NEW truth — then stop.
Settings: The Gap apartment, empty hallway, bathroom mirror, bedroom doorway, fullscreen CCTV, alarm clock at 3:12 AM.
Threat: the recording is late — motion boxes, delayed reflections, impossible doors, a human shape where no one stood.
Not this world: phone screens, cosy self-help, creature suits, animal cruelty, random static with no story, faceless advice narrator.
{horror_lane_compact()}"""


def world_lore_for_scripts() -> str:
    """Script writer context — structure + world laws."""
    return f"""{world_rules_compact()}

{black_mirror_script_structure()}

Write each Short as first-person/camera-owned screenplay — no off-screen advice narrator.
Camera Shorts must make the first impossible visual readable in the opening seconds.
Apartment Shorts: the camera sees the wrongness before the person does."""


def world_visual_continuity() -> str:
    """Paste into every video / image prompt after visual DNA."""
    return (
        "WORLD — Peripheral / The Gap: alone-at-night apartment, empty hallway, bathroom mirror, "
        "bedroom doorway, fullscreen CCTV feed, alarm clock stuck near 3:12 AM; the recording lags "
        "behind reality by one beat; partial faces and silhouettes only until the final scare; "
        "black, cold blue, dirty night-vision green, VHS/CCD grain; no phone screens, no creature suits."
    )


def world_motifs() -> tuple[str, ...]:
    """Recurring in-universe tokens for topic/QC checks."""
    return (
        "cctv",
        "security camera",
        "recording",
        "motion",
        "alarm clock",
        "3:12",
        "mirror",
        "reflection",
        "hallway",
        "doorway",
        "apartment",
        "night vision",
        "lag",
        "rec",
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
