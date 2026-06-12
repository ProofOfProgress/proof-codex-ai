from __future__ import annotations

from pathlib import Path

from shorts_bot.brand.youtube_copy import YouTubeCopyFields, parse_youtube_copy
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
        self.world_path = Path("channel/brand/world.md")

    def voice(self) -> str:
        if self.voice_path.exists():
            return self.voice_path.read_text(encoding="utf-8").strip()
        return ""

    def identity_summary(self) -> str:
        if self.identity_path.exists():
            text = self.identity_path.read_text(encoding="utf-8")
            return text[:2500]
        return (
            "Channel: Peripheral — faceless horror Shorts (~30s). "
            "Jumpscare at the end. Merch tagline: don't blink. Watch the whole thing."
        )

    def youtube_copy(self) -> str:
        if self.copy_path.exists():
            return self.copy_path.read_text(encoding="utf-8").strip()
        return ""

    def youtube_fields(self) -> YouTubeCopyFields:
        parsed = parse_youtube_copy(self.youtube_copy())
        if parsed.channel_name:
            return parsed
        return YouTubeCopyFields(
            channel_name=settings.youtube_channel_name,
            description=parsed.description,
            tagline=parsed.tagline or settings.channel_tagline,
            pinned_comment=parsed.pinned_comment,
        )

    def world_summary(self) -> str:
        from shorts_bot.production.world import world_summary_for_brand

        return world_summary_for_brand()

    def draft_instructions(self) -> str:
        parts = [self.identity_summary()]
        if self.world_path.exists():
            parts.append("WORLD BIBLE (The Gap — same universe every Short):\n" + self.world_summary())
        v = self.voice()
        if v:
            parts.append("BRAND VOICE RULES:\n" + v)
        return "\n\n".join(parts)
