"""Peripheral shared universe — The Gap analog haunting."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.black_mirror_format import (
    black_mirror_format_compact,
    black_mirror_script_structure,
)
from shorts_bot.production.horror_lane import HORROR_LANE_LABEL, horror_lane_compact

WORLD_NAME = "The Gap"
WORLD_TAGLINE = "The recording lags behind reality — and catches what your eyes miss."

_WORLD_DOC = Path("channel/brand/world.md")


def world_doc_path() -> Path:
    return _WORLD_DOC


def world_rules_compact() -> str:
    """Short rules block for prompts (scripts + agents)."""
    return f"""UNIVERSE — Peripheral (~30s nightmare Shorts):
{WORLD_TAGLINE}
{black_mirror_format_compact()}
Laws: second-person or first-person immediacy; no cosy narrator; recordings lag reality; 3:12 AM is the glitch hour; what moves in peripheral vision becomes real on replay.
Twist rewrites hook; finale sting on NEW truth — then stop.
Settings: alone-at-night apartment (primary) — CCTV camera, mirror, closet, hallway, alarm clock. No phone-screen storytelling.
Threat: the thing in the recording — edge-of-frame motion, replay mismatch, final jumpscare reveal.
Not this world: cosy self-help, village cult lore, folk ritual, generic creature showcase, gore.
{horror_lane_compact()}"""


def world_lore_for_scripts() -> str:
    """Script writer context — structure + world laws."""
    return f"""{world_rules_compact()}

{black_mirror_script_structure()}

Write each Short as a concrete analog-horror micro-story with a visible recording/proof object.
Security-camera Shorts use fullscreen CCTV, not phone screens.
Every Short needs a final jumpscare beat that changes what the hook meant."""


def world_visual_continuity() -> str:
    """Paste into every video / image prompt after visual DNA."""
    return (
        "WORLD — Peripheral / The Gap: alone-at-night apartment, fullscreen CCTV, alarm clock, "
        "mirror, closet, hallway corner, door crack; reality and recording disagree; "
        "night-vision green, cold blue-black shadows, dirty monitor glow; final synced jumpscare; "
        "no phone-screen storytelling, no cosy self-help, no generic monster showcase."
    )


def world_motifs() -> tuple[str, ...]:
    """Recurring in-universe tokens for topic/QC checks."""
    return (
        "cctv",
        "security camera",
        "recording",
        "replay",
        "mirror",
        "closet",
        "hallway",
        "apartment",
        "alarm clock",
        "3:12",
        "glitch",
        "peripheral",
        "motion",
        "uncanny",
        "premise",
        "twist",
        "don't blink",
    )


def world_summary_for_brand() -> str:
    """Loaded by ChannelBrand when world.md exists."""
    if _WORLD_DOC.exists():
        text = _WORLD_DOC.read_text(encoding="utf-8").strip()
        return text[:1200]
    return world_rules_compact()
