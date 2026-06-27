"""Saved image prompts for bubble wrap production — one generation each, no regen."""

from __future__ import annotations

ORANGE_SLIDESHOW = {
    "subject": "orange",
    "subject_rules": [
        "Whole ripe orange fruit only",
        "Exactly one single even layer of clear bubble wrap",
        "Uniform small bubbles, tight smooth coverage",
        "No double layers, no extra wrap, no plastic over plastic",
    ],
    "reference_layout": {
        "hook_sample": "bubble wrap7.png",
        "cta_sample": "bubble wrap10.png",
    },
    "slide1_hook": {
        "role": "hook_only",
        "prompt": (
            "Vertical 9:16 photorealistic smartphone product photo. Close-up of a whole ripe "
            "orange fruit completely wrapped in exactly ONE single even layer of clear bubble "
            "wrap with uniform small air bubbles, smooth tight coverage, no double wrapping, "
            "no extra layers. Centered on a neutral soft gray background. Bright even studio "
            "lighting, sharp focus, satisfying ASMR aesthetic. No text, no captions, no "
            "watermark, no logo, no hands, no fingers, no people."
        ),
        "caption_overlay": ["ORANGE BUBBLE WRAP", "ASMR >>>"],
    },
    "slide2_cta": {
        "role": "interaction_poke",
        "prompt": (
            "Vertical 9:16 photorealistic smartphone product photo. Close-up of the same whole "
            "ripe orange fruit wrapped in exactly ONE single even layer of clear bubble wrap. "
            "A human index finger enters from the upper right corner pressing and poking into "
            "the bubble wrap surface, visible indent at the poke point. Neutral soft gray "
            "background, bright studio lighting, sharp focus, satisfying ASMR aesthetic. "
            "No text, no captions, no watermark, no logo."
        ),
        "caption_overlay": [
            "Pause = Pop 💥",
            "Follow = Loud pop 🔊",
            "Share = Giant pop 🦖",
            "Comment = Big pop 💥💥",
        ],
    },
    "policy": {
        "regenerations_allowed": 0,
        "format": "2-image TikTok photo carousel (not video)",
        "sound_manual": "Mackenzie sound added in TikTok app after upload",
    },
}
