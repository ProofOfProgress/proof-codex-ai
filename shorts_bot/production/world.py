"""Peripheral shared universe — The Gap analog apartment horror."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.black_mirror_format import (
    black_mirror_format_compact,
    black_mirror_script_structure,
)
from shorts_bot.production.horror_lane import HORROR_LANE_LABEL, horror_lane_compact

WORLD_NAME = "The Gap"
WORLD_TAGLINE = "Reality lags behind its recordings."

_WORLD_DOC = Path("channel/brand/world.md")


def world_doc_path() -> Path:
    return _WORLD_DOC


def world_rules_compact() -> str:
    """Short rules block for prompts (scripts + agents)."""
    return f"""UNIVERSE — Peripheral (~30s nightmare Shorts):
{WORLD_TAGLINE}
{black_mirror_format_compact()}
Laws: first-person I; fullscreen Analog/CCTV grammar; recordings reveal the wrong detail before reality does; no phone screens.
Twist rewrites hook; finale sting on NEW truth — then stop.
Settings: alone-at-night apartment, hallway, mirror, closet, empty living room, security cam corners, alarm clock at 3:12 AM.
Threat: the lag in reality — motion boxes, delayed reflections, impossible timestamps, peripheral movement.
Not this world: phone-screen storytelling, cosy self-help, creature lore dumps, village cult worship.
{horror_lane_compact()}"""


def world_lore_for_scripts() -> str:
    """Script writer context — structure + world laws."""
    return f"""{world_rules_compact()}

{black_mirror_script_structure()}

Write each Short as first-person screenplay — victim sees proof in the room or recording.
Security-camera Shorts: fullscreen CCTV, REC OSD/alarm-clock time only, no phone UI.
Apartment Shorts: one concrete wrong detail, false calm, then the jumpscare stops the Short."""


def world_visual_continuity() -> str:
    """Paste into every video / image prompt after visual DNA."""
    return (
        "WORLD — Peripheral / The Gap: alone-at-night apartment, fullscreen CCTV angles, "
        "alarm clock or REC OSD at 3:12 AM, empty hallway, mirror, closet, cold living room; "
        "reality lags behind recordings by one impossible beat; dirty night-vision green, "
        "cold blue-black shadows, crimson only on the final sting; no phone screens."
    )


def world_motifs() -> tuple[str, ...]:
    """Recurring in-universe tokens for topic/QC checks."""
    return (
        "cctv",
        "security camera",
        "recording",
        "rec",
        "motion",
        "lag",
        "3:12",
        "alarm clock",
        "apartment",
        "hallway",
        "mirror",
        "closet",
        "empty room",
        "night vision",
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
