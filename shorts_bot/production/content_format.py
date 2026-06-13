"""Content format profiles — Shorts discovery + long-form without runaway I2V cost."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ContentFormatId = Literal[
    "short_30",
    "short_hybrid",
    "long_compilation",
    "long_still",
    "long_hybrid",
]


@dataclass(frozen=True)
class ContentFormatProfile:
    """Per-format production contract — duration, aspect, I2V budget."""

    id: ContentFormatId
    label: str
    aspect_ratio: str  # 9:16 | 16:9
    target_duration_seconds: tuple[float, float]
    max_i2v_beats: int
    visual_style: str  # ai_video | hybrid | still
    reuse_short_clips: bool
    description: str

    @property
    def is_long_form(self) -> bool:
        return self.id.startswith("long_")


PROFILES: dict[ContentFormatId, ContentFormatProfile] = {
    "short_30": ContentFormatProfile(
        id="short_30",
        label="Short (~30s)",
        aspect_ratio="9:16",
        target_duration_seconds=(25.0, 40.0),
        max_i2v_beats=2,
        visual_style="ai_video",
        reuse_short_clips=False,
        description="Launch Short — Kling 2×15s native audio (default) or legacy I2V.",
    ),
    "short_hybrid": ContentFormatProfile(
        id="short_hybrid",
        label="Short hybrid (low cost)",
        aspect_ratio="9:16",
        target_duration_seconds=(25.0, 40.0),
        max_i2v_beats=3,
        visual_style="hybrid",
        reuse_short_clips=False,
        description="Hook + finale I2V; middle beats Ken Burns stills — ~70% cost cut.",
    ),
    "long_compilation": ContentFormatProfile(
        id="long_compilation",
        label="Long compilation (stitch Shorts)",
        aspect_ratio="16:9",
        target_duration_seconds=(480.0, 900.0),
        max_i2v_beats=0,
        visual_style="still",
        reuse_short_clips=True,
        description="3–5 published Shorts + bridge VO; zero new Replicate I2V.",
    ),
    "long_still": ContentFormatProfile(
        id="long_still",
        label="Long still narrative",
        aspect_ratio="16:9",
        target_duration_seconds=(300.0, 720.0),
        max_i2v_beats=0,
        visual_style="still",
        reuse_short_clips=False,
        description="5–12 min VO over FLUX stills + Ken Burns; no I2V.",
    ),
    "long_hybrid": ContentFormatProfile(
        id="long_hybrid",
        label="Long hybrid (hero motion)",
        aspect_ratio="16:9",
        target_duration_seconds=(480.0, 900.0),
        max_i2v_beats=4,
        visual_style="hybrid",
        reuse_short_clips=True,
        description="Reuse Short clips as B-roll; 2–4 new landscape hero I2V beats max.",
    ),
}


def profile_for(format_id: str | None = None) -> ContentFormatProfile:
    from shorts_bot.config import settings

    key = (format_id or settings.content_format or "short_30").strip().lower()
    if key not in PROFILES:
        return PROFILES["short_30"]
    return PROFILES[key]  # type: ignore[index]


def effective_max_i2v_beats(*, format_id: str | None = None) -> int:
    """Cap Replicate I2V calls — format profile overrides global ai_video_max_beats."""
    from shorts_bot.config import settings

    prof = profile_for(format_id)
    cap = min(prof.max_i2v_beats, int(settings.ai_video_max_beats))
    if prof.visual_style == "still" or prof.max_i2v_beats == 0:
        return 0
    return max(0, cap)


def effective_visual_style(*, format_id: str | None = None) -> str:
    prof = profile_for(format_id)
    if prof.max_i2v_beats == 0:
        return "still"
    return prof.visual_style
