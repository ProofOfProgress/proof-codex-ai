"""Peripheral horror subgenre lane — analog CCTV horror."""

from __future__ import annotations

HORROR_LANE_PRIMARY = "analog_horror"
HORROR_LANE_LABEL = "Analog CCTV horror"

HORROR_LANE_SECONDARY = "apartment_recording_lag"

HORROR_LANES_REJECTED = (
    "faceless_narrator_pov",
    "creature_horror",
    "folk_horror",
    "slasher_gore",
    "cosmic_horror",
    "real_world_religion_mockery",
    "animal_cruelty",
)

HORROR_LANE_TERTIARY = "peripheral_jumpscare"


def horror_lane_compact() -> str:
    """Inject into script + agent prompts."""
    from shorts_bot.production.metal_aesthetic import metal_aesthetic_compact

    return f"""HORROR LANE — {HORROR_LANE_LABEL} (primary) + apartment recording lag (secondary) + peripheral jumpscare (tertiary):
Analog: fullscreen CCTV/night-vision footage, REC OSD or alarm-clock time, cold apartment corners, no phone screens.
Recording lag: cameras show one impossible detail a second before reality catches up.
Peripheral: wrong movement at the edge of frame; final beat snaps toward camera, then STOP.
{metal_aesthetic_compact()}
Color: black, cold blue-black (#1A2A3A), dirty night-vision green, crimson accent on finale only.
Never: phone screens, readable fake UI text, cosy aesthetic, creature reveals, animal cruelty, gore.
Rejected: {", ".join(HORROR_LANES_REJECTED)}."""


def analog_color_rules() -> str:
    """Analog CCTV palette for prompts."""
    return (
        "COLOR RULE: analog night-vision green, crushed blacks, cold blue-black shadows; "
        "crimson accent sparingly on finale; VHS/CCTV grain and underexposed corners."
    )


def horror_lane_for_qc() -> str:
    """Production review context."""
    from shorts_bot.production.black_mirror_format import black_mirror_for_qc

    return (
        f"Channel lane: {HORROR_LANE_LABEL} inside Peripheral (The Gap). "
        f"{black_mirror_for_qc()} "
        "Score fullscreen CCTV/night-vision dread, recording lag, and final jumpscare timing. "
        "Penalize phone screens, readable fake UI text, creature reveals, and off-screen narrator mismatch."
    )
