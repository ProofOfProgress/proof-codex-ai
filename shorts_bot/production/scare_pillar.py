"""PERIPHERAL scare pillar classification — rotate types across uploads."""

from __future__ import annotations

PILLARS = (
    "the_test",
    "the_rite",
    "the_witness",
    "the_periphery",
    "the_architect",
)


def scare_pillar_for_topic(topic: str) -> str:
    lower = (topic or "").lower()
    if any(k in lower for k in ("architect", "choice", "test", "trap", "tape", "countdown", "chain")):
        return "the_test"
    if any(k in lower for k in ("rite", "ritual", "chant", "circle", "forest", "hood", "offering", "blood-eagle", "eagle")):
        return "the_rite"
    if any(k in lower for k in ("security", "camera", "cctv", "footage", "witness", "cam")):
        return "the_witness"
    if any(k in lower for k in ("eye", "peripheral", "periphery", "frame", "blink", "reflection", "mirror")):
        return "the_periphery"
    if any(k in lower for k in ("architect", "voice", "symbol", "carved", "rule")):
        return "the_architect"
    return "the_test"


def pillar_label(pillar: str) -> str:
    return {
        "the_test": "The test",
        "the_rite": "The rite",
        "the_witness": "The witness",
        "the_periphery": "The periphery",
        "the_architect": "The Architect",
    }.get(pillar, pillar)
