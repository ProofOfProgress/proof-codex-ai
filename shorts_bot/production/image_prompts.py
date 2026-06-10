from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shorts_bot.production.framing import framing_notes_for_prompt
from shorts_bot.production.turboscribe_parser import TranscriptSegment


@dataclass
class ImageBrief:
    start_seconds: float
    end_seconds: float
    filename_stem: str
    spoken_text: str
    prompt: str


def _load_style_guide() -> str:
    from shorts_bot.config import settings

    if settings.visual_style == "stickfigure":
        path = Path("channel/brand/stick_figure_style.md")
        if path.exists():
            return path.read_text(encoding="utf-8").strip()
        return (
            "ChainsFR-style stick figures on off-white #F4F4F0, black line art, "
            "character ACTING OUT each beat, speech bubbles only for quoted dialogue."
        )
    path = Path("channel/brand/still_image_style.md")
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return "Calm faceless 9:16 still, soft continuity aesthetic, no text on image."


def build_master_prompt(*, channel_topic: str = "Soft Continuity self-help Short") -> str:
    style = _load_style_guide()
    from shorts_bot.config import settings

    format_line = (
        "Every prompt: ChainsFR-style stick figure ACTING the line, off-white background, "
        "speech bubble only for quoted dialogue."
        if settings.visual_style == "stickfigure"
        else 'Every prompt must end with: "vertical 9:16 still image, no text, no watermark, faceless."'
    )
    return f"""You are generating frame images for a faceless YouTube Short on channel "{channel_topic}".

RULES (critical):
1. Read the timestamped script below.
2. Create ONE image prompt for EACH timestamp block.
3. Each image covers only the words from that timestamp until the next timestamp.
4. Output prompts as JSON array: [{{"timestamp": "00.07", "prompt": "..."}}]

STYLE (Soft Continuity):
{style[:2000]}

{format_line}

TIMESTAMPED SCRIPT:
(paste TurboScribe export below)
"""


def segment_to_prompt(seg: TranscriptSegment, *, topic: str) -> str:
    from shorts_bot.production.stick_background import plan_room

    scene = seg.text.strip() or topic
    room = plan_room(scene)
    bg = room.background.value.replace("_", " ")
    props = ", ".join(room.wall_props) if room.wall_props else "plant, clock"
    return (
        f"ChainsFR stick figure on THE SAME COUCH: {scene}. Topic: {topic}. "
        f"Background behind couch: {bg} with {props}. "
        "MS-Paint-simple line art, off-white room, black stick figure ACTING the line. "
        "Speech bubble ONLY for quoted dialogue. Couch geometry identical every frame. "
        "No photorealism, no 3D, no cinematic lighting."
    )


def ai_segment_to_prompt(seg: TranscriptSegment, *, topic: str) -> str:
    """Paid image generator prompt — Soft Continuity calm stills."""
    style = _load_style_guide()
    scene = seg.text.strip() or topic
    return (
        f"Calm faceless self-help still frame: {scene}. "
        f"Channel topic: {topic}. "
        "Mood: quiet room, soft window light, minimal composition, generous negative space. "
        "One symbolic element max (thin ring, faint glow, silhouette). "
        "Palette: deep navy #0B1020, mist blue #8EB8FF, warm white accents. "
        "No human faces, no celebrity likeness, no horror, no robots. "
        f"{framing_notes_for_prompt()} "
        "vertical 9:16 still image, no text, no watermark, faceless, soft continuity aesthetic. "
        f"Style notes: {style[:400]}"
    )


def build_image_briefs(
    segments: list[TranscriptSegment],
    *,
    topic: str,
    total_duration: float | None = None,
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
        from shorts_bot.config import settings

        prompt_fn = ai_segment_to_prompt if settings.visual_style == "ai" else segment_to_prompt
        briefs.append(
            ImageBrief(
                start_seconds=seg.start_seconds,
                end_seconds=end,
                filename_stem=stem,
                spoken_text=seg.text,
                prompt=prompt_fn(seg, topic=topic),
            )
        )
    return briefs
