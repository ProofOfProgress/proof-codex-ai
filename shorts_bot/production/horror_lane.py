"""Peripheral horror subgenre lane — analog / CCTV haunting."""

from __future__ import annotations

HORROR_LANE_PRIMARY = "analog_horror"
HORROR_LANE_LABEL = "Analog CCTV horror"

HORROR_LANE_SECONDARY = "apartment_glitch"

HORROR_LANES_REJECTED = (
    "faceless_narrator_pov",
    "creature_horror",
    "folk_horror",
    "slasher_gore",
    "cosmic_horror",
    "real_world_religion_mockery",
    "animal_cruelty",
)

HORROR_LANE_TERTIARY = "peripheral_motion"


def horror_lane_compact() -> str:
    """Inject into script + agent prompts."""
    from shorts_bot.production.metal_aesthetic import metal_aesthetic_compact

    return f"""HORROR LANE — {HORROR_LANE_LABEL} (primary) + apartment glitch (secondary) + peripheral motion (tertiary):
CCTV: fullscreen security footage, night-vision, REC overlays, empty rooms that change when replayed.
Apartment: alone-at-night domestic spaces, door cracks, closets, mirrors, hallway corners, alarm clocks.
Peripheral: something moves at the edge of frame; reality lags behind the recording; final beat is a jumpscare.
{metal_aesthetic_compact()}
Color: night-vision green, cold blue-black (#1A2A3A), dirty monitor glow; crimson accent on finale only.
Never: phone-screen storytelling, safe lifestyle aesthetic, generic monster reveals, faceless narrator, gore.
Rejected: {", ".join(HORROR_LANES_REJECTED)}."""


def analog_color_rules() -> str:
    """Legacy hook — analog CCTV palette."""
    return (
        "COLOR RULE: night-vision green CCTV wash, cold blue-black shadows, dirty monitor whites; "
        "crimson accent sparingly on final scare only; avoid warm safe interiors."
    )


def horror_lane_for_qc() -> str:
    """Production review context."""
    from shorts_bot.production.black_mirror_format import black_mirror_for_qc

    return (
        f"Channel lane: {HORROR_LANE_LABEL} inside Peripheral (The Gap). "
        f"{black_mirror_for_qc()} "
        "Score fullscreen CCTV, night-vision dread, peripheral motion, and a synced final jumpscare. "
        "Penalize phone UI, safe self-help, generic creature shots, and off-screen narrator mismatch."
    )
