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
Analog: fullscreen night-vision CCTV, VHS grain, timestamp glitches, alarm clock at 3:12 AM, degraded signal, liminal apartment.
Psychological: alone-at-night uncanny — you rationalize lag as glitch/tired eyes; earned dread, not jump-scare spam.
Color grammar: night-vision green on fullscreen fixed CCTV POV; no smartphones. POV room shots (locks, speaker) stay cold blue-black (#1A2A3A) with alarm clock for time.
Never: creature features, occult rituals, folklore names, gore, daylight crowds, cosy aesthetic.
Rejected lanes for this channel: {", ".join(HORROR_LANES_REJECTED)}."""


def analog_color_rules() -> str:
    """I2V / image prompt fragment — fixes Gemini 'random green tint' failures."""
    return (
        "ANALOG COLOR RULE: night-vision green grain ONLY on full-frame fixed CCTV/wall cam POV — "
        "no smartphones, no hands holding phones. POV room shots (locks, speaker) stay cold blue-black. "
        "Match prior clip palette when chained."
    )


def horror_lane_for_qc() -> str:
    """Production review context — score analog consistency, not generic horror."""
    return (
        f"Channel lane: {HORROR_LANE_LABEL} inside universe 'The Gap'. "
        "Intentional night-vision green on fullscreen CCTV beats is correct; "
        "no phone screens expected. Alarm clock and REC OSD are composited in post. "
        "Penalize smartphones, hands holding phones, or fake app UI."
    )
