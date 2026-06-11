"""Don't Blink horror subgenre lane — one clear type, enforced in prompts + QC."""

from __future__ import annotations

# Primary lane: degraded recordings, CCTV, night vision, phone feeds, signal lag
HORROR_LANE_PRIMARY = "analog_horror"
HORROR_LANE_LABEL = "Analog horror"

# Secondary flavor — uncanny alone-at-night dread, not creature gore
HORROR_LANE_SECONDARY = "psychological_horror"

# Lanes we explicitly do NOT pursue (keeps channel identity sharp)
HORROR_LANES_REJECTED = (
    "creature_horror",
    "occult_horror",
    "folk_horror",
    "folklore_horror",
    "urban_fantasy",
    "slasher_gore",
    "cosmic_horror",
)


def horror_lane_compact() -> str:
    """Inject into script + agent prompts."""
    return f"""HORROR LANE — {HORROR_LANE_LABEL} (primary) + psychological (secondary):
Analog: night-vision CCTV, security-app phone feeds, VHS grain, timestamp glitches, degraded signal, liminal apartment at 3:12 AM.
Psychological: alone-at-night uncanny — you rationalize lag as glitch/tired eyes; earned dread, not jump-scare spam.
Color grammar: night-vision green ONLY on wall-mounted CCTV POV or inside the phone-screen rectangle; POV room/hallway shots stay cold blue-black (#1A2A3A).
Never: creature features, occult rituals, folklore names, gore, daylight crowds, cosy aesthetic.
Rejected lanes for this channel: {", ".join(HORROR_LANES_REJECTED)}."""


def analog_color_rules() -> str:
    """I2V / image prompt fragment — fixes Gemini 'random green tint' failures."""
    return (
        "ANALOG COLOR RULE: night-vision green grain ONLY on (a) full-frame fixed CCTV/wall cam POV "
        "or (b) the rectangular phone-screen feed area — never wash the entire POV hallway in green. "
        "Hands/room around a phone stay cold blue-black underexposed. Match prior clip palette when chained."
    )


def horror_lane_for_qc() -> str:
    """Production review context — score analog consistency, not generic horror."""
    return (
        f"Channel lane: {HORROR_LANE_LABEL} inside universe 'The Gap'. "
        "Intentional night-vision green on CCTV/phone-feed beats is correct; "
        "penalize only if green bleeds onto POV room shots or palette jumps without a feed cut. "
        "Phone UI is composited in post — judge containment inside screen rect, not missing bezel."
    )
