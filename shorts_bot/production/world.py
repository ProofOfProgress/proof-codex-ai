"""Peripheral shared universe — village Eye worship."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.black_mirror_format import (
    black_mirror_format_compact,
    black_mirror_script_structure,
)
from shorts_bot.production.horror_lane import HORROR_LANE_LABEL, horror_lane_compact

WORLD_NAME = "The Village"
WORLD_TAGLINE = "They worship the Eye — it finds you in your dreams."

_WORLD_DOC = Path("channel/brand/world.md")


def world_doc_path() -> Path:
    return _WORLD_DOC


def world_rules_compact() -> str:
    """Short rules block for prompts (scripts + agents)."""
    return f"""UNIVERSE — Peripheral (~30s nightmare Shorts):
{WORLD_TAGLINE}
{black_mirror_format_compact()}
Laws: first-person I; character voices on screen only (no narrator); victims remember dreams; Eye true form in dreams; villagers worship the Eye; uncanny human wrongness when awake.
Twist rewrites hook; finale sting on NEW truth — then stop.
Settings: fog village (primary) — square, signpost, barn symbols, ritual candles. No apartment/CCTV/glitch hour.
Threat: the Eye — true form (macro eye), dream torturer, perception breaker. Villagers complicit in worship.
Not this world: security cameras, The Gap apartment, 3:12 AM glitch spam, faceless second-person narrator, cosy self-help.
{horror_lane_compact()}"""


def world_lore_for_scripts() -> str:
    """Script writer context — structure + world laws."""
    return f"""{world_rules_compact()}

{black_mirror_script_structure()}

Write each Short as first-person screenplay — CHARACTER lines only, victim speaks as I.
Dream Shorts must include waking beat where victim remembers the Eye.
Village Shorts: worship, silence, wrong villagers, ritual symbols — outsiders break the rule."""


def world_visual_continuity() -> str:
    """Paste into every video / image prompt after visual DNA."""
    return (
        "WORLD — Peripheral fog village: dusk, bone fog, crooked signpost, barn Eye symbols, "
        "villagers with averted eyes and ritual candles; dream sequences — surreal rooms, "
        "macro freaky Eye filling ceiling or mirror; waking — uncanny almost-human villagers, "
        "twitchy rabies-wrong movement; solid white and cold blue-black palette; "
        "cinematic horror — no CCTV green, no smartphones, no apartment hallway spam."
    )


def world_motifs() -> tuple[str, ...]:
    """Recurring in-universe tokens for topic/QC checks."""
    return (
        "eye",
        "the eye",
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
