from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shorts_bot.drafts.meta import visual_beat_for_segment
from shorts_bot.production.framing import framing_notes_for_prompt, screen_text_prompt_note
from shorts_bot.production.turboscribe_parser import TranscriptSegment
from shorts_bot.production.visual_identity import face_eye_visibility_rules
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
        "film grain, hallways mirrors shadows CCTV alarm clock, no cosy aesthetic."
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
    """Paid image keyframe — route crayon lane to Recraft comedy-horror prompts."""
    from shorts_bot.config import settings

    provider = (settings.image_provider or "").strip().lower()
    if provider == "recraft":
        return comedy_horror_drawn_segment_to_prompt(seg, topic=topic, visual_beat=visual_beat)
    return _photoreal_horror_segment_to_prompt(seg, topic=topic, visual_beat=visual_beat)


def comedy_horror_drawn_segment_to_prompt(
    seg: TranscriptSegment,
    *,
    topic: str,
    visual_beat: str | None = None,
) -> str:
    """Smiling Friends lane — cute crayon comedy that can snap to nightmare."""
    scene = seg.text.strip() or topic
    beat_line = f"Shot direction: {visual_beat}. " if visual_beat else ""
    scary = any(
        w in scene.lower()
        for w in (
            "run",
            "scream",
            "demon",
            "creature",
            "monster",
            "oh no",
            "don't look",
            "stop",
            "wrong",
            "isn't arms",
            "aren't arms",
            "bushes",
            "laugh",
        )
    )
    mood = (
        "sudden terrifying demon creature, wide mouth, wrong limbs, horror snap, dark forest"
        if scary
        else "goofy smiling friends vibe, casual hiking comedy, bright naive cartoon energy"
    )
    return (
        f"Hand-drawn crayon marker illustration still: {scene}. "
        f"{beat_line}"
        f"Story: {topic}. "
        f"Mood: {mood}. "
        "Setting: pine forest trail, cartoon trees, doodle bushes, Smiling Friends comedy-horror tone. "
        "Style: naive MS Paint crayon characters, thick outlines, expressive faces, slightly ugly-cute. "
        "vertical 9:16 still image, no text, no watermark, no photorealism."
    )


def _photoreal_horror_segment_to_prompt(
    seg: TranscriptSegment,
    *,
    topic: str,
    visual_beat: str | None = None,
) -> str:
    """Paid image/I2V keyframe — Don't Blink photoreal horror."""
    style = _load_style_guide()
    scene = seg.text.strip() or topic
    beat_line = f"Shot direction: {visual_beat}. " if visual_beat else ""
    return (
        f"Terrifying faceless horror still frame: {scene}. "
        f"{beat_line}"
        f"Story: {topic}. "
        "Mood: uncanny, dread, something is wrong, cinematic horror movie still. "
        "Setting: dark hallway, mirror, fullscreen security cam POV, alarm clock nightstand, shadows. "
        f"{world_visual_continuity()} "
        "Palette: black, cold blue, deep crimson, film grain, harsh contrast. "
        f"{face_eye_visibility_rules()} "
        "No gore, no blood spray. "
        f"{framing_notes_for_prompt()} "
        f"{screen_text_prompt_note()} "
        "CRITICAL: zero smartphones, zero human hands, zero mobile devices in frame. "
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
