"""Retired scare pillar — neutral stub for upload guard."""

from __future__ import annotations


def scare_pillar_for_topic(topic: str) -> str:
    return "ai_product_review"


def pillar_label(pillar: str) -> str:
    return pillar.replace("_", " ").title()
