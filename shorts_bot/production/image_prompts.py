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

    if settings.visual_style in ("ai_video", "ai", "hybrid", "ai_video_hook"):
        path = Path("channel/brand/horror_visual_style.md")
        if path.exists():
            return path.read_text(encoding="utf-8").strip()
        return (
            "Terrifying faceless horror 9:16, cinematic, cold blue-black palette, "
            "film grain, hallways mirrors shadows phones, no cosy aesthetic."
        )
    if settings.visual_style in ("stickfigure",):
        path = Path("channel/brand/stick_figure_style.md")
        if path.exists():
            return path.read_text(encoding="utf-8").strip()
        return (
            "ChainsFR-style stick figures on warm cream #F5EFE6, cosy domestic sets "
            "(lamp, rainy window, couch, mug), soft black line art, character ACTING each beat."
        )
    path = Path("channel/brand/still_image_style.md")
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return "Calm faceless 9:16 still, soft continuity aesthetic, no text on image."


def build_master_prompt(*, channel_topic: str = "Soft Continuity self-help Short") -> str:
    style = _load_style_guide()
    from shorts_bot.config import settings

    format_line = (
        "Every prompt: ChainsFR-style stick figure ACTING the line, warm cosy home background, "
        "speech bubble only for quoted dialogue."
        if settings.visual_style in ("stickfigure",)
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
    extras = []
    if room.wall_props:
        extras.append(", ".join(room.wall_props))
    if room.furniture:
        extras.append(room.furniture)
    if room.foreground_prop:
        extras.append(room.foreground_prop)
    detail = f" — {', '.join(extras)}" if extras else " — plain off-white, figure only"
    return (
        f"ChainsFR stick figure ACTING: {scene}. Topic: {topic}. "
        f"Minimal scene: {bg}{detail}. "
        "MS-Paint line art on warm cream, cosy lamp/window/couch when relevant, expressive pose. "
        "Only props the line mentions. Speech bubble ONLY for quoted dialogue. "
        "No photorealism, no 3D, no repeated couch every frame."
    )


def horror_segment_to_prompt(seg: TranscriptSegment, *, topic: str) -> str:
    """Paid image/I2V keyframe — Don't Blink horror."""
    style = _load_style_guide()
    scene = seg.text.strip() or topic
    return (
        f"Terrifying faceless horror still frame: {scene}. "
        f"Story: {topic}. "
        "Mood: uncanny, dread, something is wrong, cinematic horror movie still. "
        "Setting: dark hallway, mirror, phone screen, empty room, security cam POV, shadows. "
        "Palette: black, cold blue, deep crimson, film grain, harsh contrast. "
        "Silhouettes only — no full face until scare beat. No gore, no blood. "
        f"{framing_notes_for_prompt()} "
        "vertical 9:16 still image, no text, no watermark, photorealistic horror, terrifying. "
        f"Style: {style[:400]}"
    )


def ai_segment_to_prompt(seg: TranscriptSegment, *, topic: str) -> str:
    """Paid image generator prompt — horror default for Don't Blink."""
    return horror_segment_to_prompt(seg, topic=topic)


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

        if settings.visual_style in ("ai", "ai_video", "hybrid", "ai_video_hook"):
            prompt_fn = horror_segment_to_prompt
        else:
            prompt_fn = segment_to_prompt
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
