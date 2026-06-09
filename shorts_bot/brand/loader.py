from __future__ import annotations

from pathlib import Path

from shorts_bot.config import settings


class ChannelBrand:
    """Loads channel brand voice and copy for drafts + agent."""

    def __init__(self, base: Path | None = None) -> None:
        root = base or settings.course_dir
        self.identity_path = root.parent / "channel" / "brand" / "identity.md"
        if not self.identity_path.exists():
            self.identity_path = Path("channel/brand/identity.md")
        self.voice_path = root / "brand" / "voice.md"
        self.copy_path = Path("channel/brand/youtube_copy.txt")

    def voice(self) -> str:
        if self.voice_path.exists():
            return self.voice_path.read_text(encoding="utf-8").strip()
        return ""

    def identity_summary(self) -> str:
        if self.identity_path.exists():
            text = self.identity_path.read_text(encoding="utf-8")
            return text[:2500]
        return "Channel: helpful faceless Shorts. Subtle warm oracle tone. No slop."

    def youtube_copy(self) -> str:
        if self.copy_path.exists():
            return self.copy_path.read_text(encoding="utf-8").strip()
        return ""

    def draft_instructions(self) -> str:
        parts = [self.identity_summary()]
        v = self.voice()
        if v:
            parts.append("BRAND VOICE RULES:\n" + v)
        return "\n\n".join(parts)
