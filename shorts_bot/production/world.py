"""Don't Blink shared universe — The Gap.

Every Short is a different night in the same liminal domestic horror world.
Inject into scripts, I2V prompts, and brand context so scares feel connected.
"""

from __future__ import annotations

from pathlib import Path

from shorts_bot.production.horror_lane import HORROR_LANE_LABEL, horror_lane_compact

WORLD_NAME = "The Gap"
WORLD_TAGLINE = "Reality and recordings are one beat out of sync."

_WORLD_DOC = Path("channel/brand/world.md")


def world_doc_path() -> Path:
    return _WORLD_DOC


def world_rules_compact() -> str:
    """Short rules block for prompts (scripts + agents)."""
    return f"""UNIVERSE — {WORLD_NAME} (Don't Blink world):
{WORLD_TAGLINE}
Laws: movement in the unwatched moment (blink, look away, refresh, mute); 3:12 AM is when systems glitch;
CCTV/mirrors/recordings show truth delayed or wrong; no phone screens in analog lane; you are alone at home tonight; faceless until final scare beat.
Setting: same liminal apartment grammar — narrow hallway, bathroom mirror, alarm clock nightstand, security cam corner, closet you never open.
Threat: the thing in the gap — never named in VO; advances when you stop watching; finale lunge from mirror/door/lens/screen.
Not this world: cosy self-help, stick figures, gore, daytime crowds, generic creepypasta listicles.
{horror_lane_compact()}"""


def world_lore_for_scripts() -> str:
    """Script writer context — structure + world laws."""
    return f"""{world_rules_compact()}

Write each Short as another night in {WORLD_NAME}, not a one-off template swap.
Prefer hooks that cite lag (timestamp, delivered-while-off, motion while alone, delayed reflection).
False calm must be in-world rationalization: glitch, lag, tired eyes, app delay — not comedy, not therapy."""


def world_visual_continuity() -> str:
    """Paste into every I2V / image prompt after visual DNA."""
    return (
        f"WORLD — {WORLD_NAME}: liminal alone-at-night apartment, narrow hallway into darkness, "
        "analog horror: cold blue-black POV rooms, night-vision green only on fullscreen CCTV; "
        "film grain, underexposed; CCTV/mirror/recordings as truth sources that lag reality; "
        "3:12 AM motif when time appears; faceless silhouettes until final lunge; "
        "same domestic grammar across uploads — not a new location every video."
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
    )


def world_summary_for_brand() -> str:
    """Loaded by ChannelBrand when world.md exists."""
    if _WORLD_DOC.exists():
        text = _WORLD_DOC.read_text(encoding="utf-8").strip()
        # First ~1200 chars covers laws + place without blowing token budgets
        return text[:1200]
    return world_rules_compact()
