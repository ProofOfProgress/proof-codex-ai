from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shorts_bot.drafts.meta import visual_beat_for_segment
from shorts_bot.production.framing import framing_notes_for_prompt, screen_text_prompt_note
from shorts_bot.production.turboscribe_parser import TranscriptSegment
from shorts_bot.production.world import world_visual_continuity


@dataclass
class ImageBrief:
    start_seconds: float
    end_seconds: float
    filename_stem: str
    spoken_text: str
    prompt: str


def _load_style_guide() -> str:
    path = Path("channel/brand/horror_visual_style.md")
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return (
        "Terrifying faceless horror 9:16, cinematic, cold blue-black palette, "
        "film grain, hallways mirrors shadows phones, no cosy aesthetic."
    )


def build_master_prompt(*, channel_topic: str = "Don't Blink horror Short") -> str:
    style = _load_style_guide()
    return f"""You are generating horror keyframe images for faceless YouTube Short "{channel_topic}".

RULES (critical):
1. Read the timestamped script below.
2. Create ONE image prompt for EACH timestamp block.
3. Each image covers only the words from that timestamp until the next timestamp.
4. Output prompts as JSON array: [{{"timestamp": "00.07", "prompt": "..."}}]

STYLE (Don't Blink — terrifying, not cosy):
{style[:2000]}

Every prompt must end with: "vertical 9:16 still image, no text, no watermark, photorealistic horror."

TIMESTAMPED SCRIPT:
(paste TurboScribe export below)
"""


def horror_segment_to_prompt(
    seg: TranscriptSegment,
    *,
    topic: str,
    visual_beat: str | None = None,
) -> str:
    """Paid image/I2V keyframe — Don't Blink horror."""
    style = _load_style_guide()
    scene = seg.text.strip() or topic
    beat_line = f"Shot direction: {visual_beat}. " if visual_beat else ""
    return (
        f"Terrifying faceless horror still frame: {scene}. "
        f"{beat_line}"
        f"Story: {topic}. "
        "Mood: uncanny, dread, something is wrong, cinematic horror movie still. "
        "Setting: dark hallway, mirror, phone screen, empty room, security cam POV, shadows. "
        f"{world_visual_continuity()} "
        "Palette: black, cold blue, deep crimson, film grain, harsh contrast. "
        "Silhouettes only — no full face until scare beat. No gore, no blood. "
        f"{framing_notes_for_prompt()} "
        f"{screen_text_prompt_note()} "
        "vertical 9:16 still image, no text, no watermark, photorealistic horror, terrifying. "
        f"Style: {style[:400]}"
    )


def ai_segment_to_prompt(seg: TranscriptSegment, *, topic: str) -> str:
    return horror_segment_to_prompt(seg, topic=topic)


def build_image_briefs(
    segments: list[TranscriptSegment],
    *,
    topic: str,
    total_duration: float | None = None,
    visual_beats: list[str] | None = None,
) -> list[ImageBrief]:
    if not segments:
        return []

    briefs: list[ImageBrief] = []
    for i, seg in enumerate(segments):
        if i + 1 < len(segments):
            end = segments[i + 1].start_seconds
        elif total_duration and total_duration > seg.start_seconds:
            end = total_duration
        else:
            end = seg.start_seconds + 5.0

        from shorts_bot.production.turboscribe_parser import label_from_seconds

        stem = label_from_seconds(seg.start_seconds)
        briefs.append(
            ImageBrief(
                start_seconds=seg.start_seconds,
                end_seconds=end,
                filename_stem=stem,
                spoken_text=seg.text,
                prompt=horror_segment_to_prompt(
                    seg,
                    topic=topic,
                    visual_beat=visual_beat_for_segment(visual_beats, i, len(segments)),
                ),
            )
        )
    return briefs
