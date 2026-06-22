"""Topic pillar for upload rotation — one pillar per product/topic slug."""

from __future__ import annotations

import re


def scare_pillar_for_topic(topic: str) -> str:
    """Unique slug per product/topic so back-to-back AI reviews don't false-block."""
    raw = (topic or "").strip().lower()
    head = re.split(r"[—\-|]", raw, maxsplit=1)[0].strip()
    slug = re.sub(r"[^a-z0-9]+", "_", head).strip("_")
    return slug[:48] or "general"


def pillar_label(pillar: str) -> str:
    return pillar.replace("_", " ").title()
