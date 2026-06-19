"""Peripheral horror subgenre lane — analog/CCTV horror."""

from __future__ import annotations

HORROR_LANE_PRIMARY = "analog_horror"
HORROR_LANE_LABEL = "Analog CCTV horror"

HORROR_LANE_SECONDARY = "the_gap_eye_lore"

HORROR_LANES_REJECTED = (
    "phone_screen_horror",
    "cctv_template_spam",
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

    return f"""HORROR LANE — {HORROR_LANE_LABEL} (primary) + The Gap / Eye lore (secondary) + uncanny perception break (tertiary):
Analog: fullscreen CCTV, night-vision hallway, REC HUD, alarm clock 3:12 AM, security motion alerts; no phone screens.
The Gap: the same alone-at-night apartment lags behind recordings; old village/Eye worship is background lore, not the default setting.
Wrongness: an empty feed reacts before reality does; reflections, masks, or eyes appear a beat late; finale jumpscare reveals the new truth.
{metal_aesthetic_compact()}
Color: black, cold blue-black (#1A2A3A), night-vision green, VHS grain; crimson accent on finale only.
Never: smartphones, phone UI, cosy aesthetic, generic creature chase, gore, animal cruelty, endless 3:12 AM spam without a twist.
Rejected: {", ".join(HORROR_LANES_REJECTED)}."""


def analog_color_rules() -> str:
    """Color rules for the current analog/CCTV lane."""
    return (
        "COLOR RULE: black + cold blue-black rooms, night-vision green CCTV wash, VHS/film grain; "
        "bone-white highlights for masks/eyes; crimson accent sparingly on finale only; "
        "avoid warm lamp glow and phone-screen blue."
    )


def horror_lane_for_qc() -> str:
    """Production review context."""
    from shorts_bot.production.black_mirror_format import black_mirror_for_qc

    return (
        f"Channel lane: {HORROR_LANE_LABEL} inside Peripheral (The Gap). "
        f"{black_mirror_for_qc()} "
        "Score fullscreen CCTV, night-vision, alarm-clock timing, clear motion-alert payoff, and final jumpscare. "
        "Penalize phone screens, generic creature chases, off-screen narrator mismatch, and repeated glitch-hour filler."
    )
