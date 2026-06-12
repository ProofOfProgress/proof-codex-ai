"""Peripheral shared universe — anthology episode grammar.

Every Short is a self-contained Black Mirror-style episode in rotating settings.
Inject into scripts, I2V prompts, and brand context so scares feel connected.
"""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.black_mirror_format import (
    black_mirror_format_compact,
    black_mirror_script_structure,
)
from shorts_bot.production.horror_lane import HORROR_LANE_LABEL, horror_lane_compact

WORLD_NAME = "The Gap"
WORLD_TAGLINE = "One rule breaks — the recording shows you the bill."

_WORLD_DOC = Path("channel/brand/world.md")


def world_doc_path() -> Path:
    return _WORLD_DOC


def world_rules_compact() -> str:
    """Short rules block for prompts (scripts + agents)."""
    return f"""UNIVERSE — Peripheral anthology (Black Mirror episode feel, ~30s each):
{WORLD_TAGLINE}
{black_mirror_format_compact()}
Laws: one broken rule in hook; consequences escalate each beat; twist rewrites line 1; finale sting on the NEW truth — then stop.
Movement in unwatched moments (blink, look away, refresh); 3:12 AM glitch hour; recordings lag reality.
Eyes & masks: macro staring eye and metal/beak masks are brand heroes — visible when earned; finale escalates.
Settings (rotate): The Gap (liminal apartment), village curse-sign (see it → slow death — implied sickness only), warehouse pit (masks/chains).
Threats never named in VO: the Lag, the Sign, the Segment — different masks, same episode grammar.
Not this world: cosy self-help, stick figures, gore, generic creepypasta listicles.
{horror_lane_compact()}"""


def world_lore_for_scripts() -> str:
    """Script writer context — structure + world laws."""
    return f"""{world_rules_compact()}

{black_mirror_script_structure()}

Write each Short as a standalone anthology episode — premise → escalation → twist → sting.
Prefer hooks that state the broken rule (village sign, timestamp, delivered-while-off, warm mask you never removed).
False calm must be in-world rationalization: glitch, lag, tired eyes, old village superstition — not comedy, not therapy."""


def world_visual_continuity() -> str:
    """Paste into every I2V / image prompt after visual DNA."""
    return (
        f"WORLD — Peripheral anthology ({WORLD_NAME} apartment thread): Black Mirror episode cinematography — clinical, cold, precise; "
        "rotate settings — liminal apartment (hallway, mirror, CCTV), fog village square (signpost, barn symbol), "
        "or warehouse pit (masks, chains, red strobe); film grain, underexposed; "
        "CCTV/mirror/recordings as truth sources that lag reality; 3:12 AM when time appears; "
        "macro eyes and masks visible when story calls for it; finale sting on twist truth — "
        "same episode grammar across uploads, not one location every video."
    )


def world_motifs() -> tuple[str, ...]:
    """Recurring in-universe tokens for topic/QC checks."""
    return (
        "3:12",
        "3:12 am",
        "3am",
        "3 am",
        "blink",
        "reflection",
        "mirror",
        "security",
        "camera",
        "motion",
        "delivered",
        "timestamp",
        "hallway",
        "closet",
        "knock",
        "muted",
        "lag",
        "glitch",
        "feed",
        "night vision",
        "alone",
        "sign",
        "village",
        "vomit",
        "sickness",
        "omen",
        "curse",
        "premise",
        "twist",
        "rule",
        "warehouse",
        "mask",
        "pit",
    )


def world_summary_for_brand() -> str:
    """Loaded by ChannelBrand when world.md exists."""
    if _WORLD_DOC.exists():
        text = _WORLD_DOC.read_text(encoding="utf-8").strip()
        return text[:1200]
    return world_rules_compact()
