"""Don't Blink scare pillar classification — rotate types across uploads (YPP + retention)."""

from __future__ import annotations

PILLARS = (
    "wrong_reflection",
    "wrong_place",
    "wrong_time",
    "wrong_sound",
    "wrong_text",
)


def scare_pillar_for_topic(topic: str) -> str:
    lower = (topic or "").lower()
    if any(k in lower for k in ("mirror", "reflection", "blink", "window wave")):
        return "wrong_reflection"
    if any(k in lower for k in ("security", "camera", "cctv", "motion", "ring", "footage")):
        return "wrong_place"
    if any(k in lower for k in ("text", "message", "autocorrect", "notification", "contact", "delivered")):
        return "wrong_text"
    if any(k in lower for k in ("timestamp", "tomorrow", "yesterday", "3am", "photo", "future")):
        return "wrong_time"
    if any(k in lower for k in ("knock", "closet", "breath", "footstep", "muted", "scratch")):
        return "wrong_sound"
    if any(k in lower for k in ("hallway", "door", "room", "elevator", "bed")):
        return "wrong_place"
    return "wrong_place"


def pillar_label(pillar: str) -> str:
    return {
        "wrong_reflection": "Wrong reflection",
        "wrong_place": "Wrong place",
        "wrong_time": "Wrong time",
        "wrong_sound": "Wrong sound",
        "wrong_text": "Wrong text",
    }.get(pillar, pillar)
