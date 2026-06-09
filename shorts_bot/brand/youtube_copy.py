from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class YouTubeCopyFields:
    channel_name: str
    description: str
    tagline: str = ""
    pinned_comment: str = ""

    def summary(self) -> str:
        parts = [f"Name: {self.channel_name}"]
        if self.description:
            parts.append(f"Description: {self.description[:80]}{'…' if len(self.description) > 80 else ''}")
        return " · ".join(parts)


_SECTION_KEYS = ("CHANNEL NAME", "DESCRIPTION", "TAGLINE", "PINNED COMMENT")


def parse_youtube_copy(text: str) -> YouTubeCopyFields:
    """Parse channel/brand/youtube_copy.txt into structured fields."""
    if not text.strip():
        return YouTubeCopyFields(channel_name="", description="")

    sections: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        matched = None
        for key in _SECTION_KEYS:
            prefix = f"{key}:"
            if line.upper().startswith(prefix):
                matched = key
                rest = line[len(prefix) :].strip()
                if current_key:
                    sections[current_key] = "\n".join(current_lines).strip()
                current_key = matched
                current_lines = [rest] if rest else []
                break
        if matched is None and current_key:
            current_lines.append(line)

    if current_key:
        sections[current_key] = "\n".join(current_lines).strip()

    name = sections.get("CHANNEL NAME", "").strip()
    description = sections.get("DESCRIPTION", "").strip()
    # Collapse extra blank lines in description but keep paragraph breaks
    if description:
        description = re.sub(r"\n{3,}", "\n\n", description)

    return YouTubeCopyFields(
        channel_name=name,
        description=description,
        tagline=sections.get("TAGLINE", "").strip(),
        pinned_comment=sections.get("PINNED COMMENT", "").strip(),
    )
