"""Peripheral horror subgenre lane — village Eye worship."""

from __future__ import annotations

HORROR_LANE_PRIMARY = "village_cult_horror"
HORROR_LANE_LABEL = "Village cult / Eye worship"

HORROR_LANE_SECONDARY = "dream_invasion"

HORROR_LANES_REJECTED = (
    "analog_cctv_spam",
    "apartment_glitch_horror",
    "faceless_narrator_pov",
    "creature_horror",
    "folk_horror",
    "slasher_gore",
    "cosmic_horror",
    "real_world_religion_mockery",
    "animal_cruelty",
)

HORROR_LANE_TERTIARY = "uncanny_perception_break"


def horror_lane_compact() -> str:
    """Inject into script + agent prompts."""
    from shorts_bot.production.metal_aesthetic import metal_aesthetic_compact

    return f"""HORROR LANE — {HORROR_LANE_LABEL} (primary) + dream invasion (secondary) + uncanny perception break (tertiary):
Village: fog dusk, villagers worship the Eye, ritual symbols, silent complicity, outsiders break rules.
Dream: Eye true form tortures victims; they remember on waking (metal taste, gasp).
Waking: uncanny almost-human villagers — twitchy, wrong speech, shape-shifting energy; Eye breaks perception.
{metal_aesthetic_compact()}
Color: fog grey, cold blue-black (#1A2A3A), crimson accent on finale only; dream Eye macro fills frame.
Never: security cameras, apartment glitch, 3:12 AM spam, smartphones, faceless narrator, cosy aesthetic.
Rejected: {", ".join(HORROR_LANES_REJECTED)}."""


def analog_color_rules() -> str:
    """Legacy hook — village palette only (no analog CCTV)."""
    return (
        "COLOR RULE: fog-grey village exteriors, cold blue-black interiors, bone white fog; "
        "crimson accent sparingly on ritual/finale; dream sequences may push surreal contrast; "
        "no night-vision green CCTV wash."
    )


def horror_lane_for_qc() -> str:
    """Production review context."""
    from shorts_bot.production.black_mirror_format import black_mirror_for_qc

    return (
        f"Channel lane: {HORROR_LANE_LABEL} inside Peripheral (The Village). "
        f"{black_mirror_for_qc()} "
        "Score village worship, Eye dream imagery, uncanny humans — not CCTV/analog glitch. "
        "Penalize security cam UI, apartment hallway spam, off-screen narrator mismatch."
    )
