"""Peripheral scare pillar classification — rotate story types across uploads."""

from __future__ import annotations

PILLARS = (
    "eye_worship",
    "dream_invasion",
    "wrong_villager",
    "outsider_rule",
    "perception_break",
)


def scare_pillar_for_topic(topic: str) -> str:
    lower = (topic or "").lower()
    if any(k in lower for k in ("dream", "woke", "remembered the eye", "metal taste", "sleep")):
        return "dream_invasion"
    if any(k in lower for k in ("worship", "ritual", "pray", "chant", "candle", "priestess")):
        return "eye_worship"
    if any(k in lower for k in ("neighbor", "villager", "teeth", "smile", "face", "uncanny", "blink")):
        return "wrong_villager"
    if any(k in lower for k in ("sign", "symbol", "barn", "name", "outsider", "square", "fog")):
        return "outsider_rule"
    if any(k in lower for k in ("sane", "speak", "reality", "schiz", "head", "perception")):
        return "perception_break"
    return "outsider_rule"


def pillar_label(pillar: str) -> str:
    return {
        "eye_worship": "Eye worship",
        "dream_invasion": "Dream invasion",
        "wrong_villager": "Wrong villager",
        "outsider_rule": "Outsider rule",
        "perception_break": "Perception break",
    }.get(pillar, pillar)
