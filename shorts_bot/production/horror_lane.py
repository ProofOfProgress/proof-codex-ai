"""Peripheral horror subgenre lane — analog surveillance horror."""

from __future__ import annotations

HORROR_LANE_PRIMARY = "analog_horror"
HORROR_LANE_LABEL = "Analog horror / CCTV anomaly"

HORROR_LANE_SECONDARY = "apartment_surveillance"

HORROR_LANES_REJECTED = (
    "random_analog_glitch_spam",
    "phone_screen_horror",
    "faceless_narrator_pov",
    "creature_horror",
    "folk_horror",
    "slasher_gore",
    "cosmic_horror",
    "real_world_religion_mockery",
    "animal_cruelty",
)

HORROR_LANE_TERTIARY = "wrong_reflection_or_recording_lag"


def horror_lane_compact() -> str:
    """Inject into script + agent prompts."""
    from shorts_bot.production.metal_aesthetic import metal_aesthetic_compact

    return f"""HORROR LANE — {HORROR_LANE_LABEL} (primary) + apartment surveillance (secondary) + wrong reflection/recording lag (tertiary):
Analog: fullscreen CCTV, night-vision, REC OSD, alarm clocks, mirrors, hallway cameras; never phone screens.
Threat: what the recording catches is behind reality by one beat — motion boxes, delayed blinks, impossible doors.
Human wrongness: silhouettes, partial faces, reflection lag, shadow at frame edge; not monster suits or creature features.
{metal_aesthetic_compact()}
Color: black, cold blue, dirty night-vision green, VHS/CCD grain; crimson accent on finale only.
Never: smartphone UI, cosy aesthetic, animal cruelty, gore, random static with no story, faceless advice narrator.
Rejected: {", ".join(HORROR_LANES_REJECTED)}."""


def analog_color_rules() -> str:
    """Analog CCTV palette rules for prompts and QC."""
    return (
        "COLOR RULE: cold blue-black shadows, dirty night-vision green only on CCTV feeds, "
        "bone-white blown highlights, VHS/CCD grain; crimson accent sparingly on finale."
    )


def horror_lane_for_qc() -> str:
    """Production review context."""
    from shorts_bot.production.black_mirror_format import black_mirror_for_qc

    return (
        f"Channel lane: {HORROR_LANE_LABEL} inside Peripheral (The Gap). "
        f"{black_mirror_for_qc()} "
        "Score fullscreen CCTV, mirror lag, night-vision dread, and final jumpscare clarity. "
        "Penalize phone screens, creature suits, animal cruelty, cosy visuals, and off-screen narrator mismatch."
    )
