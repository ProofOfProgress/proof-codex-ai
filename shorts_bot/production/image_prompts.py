from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shorts_bot.drafts.meta import visual_beat_for_segment
from shorts_bot.production.framing import framing_notes_for_prompt, screen_text_prompt_note
from shorts_bot.production.turboscribe_parser import TranscriptSegment
from shorts_bot.production.visual_identity import face_eye_visibility_rules
from shorts_bot.production.world import world_visual_continuity


COMEDY_HORROR_SCARY_KEYWORDS = (
    "run",
    "scream",
    "demon",
    "creature",
    "monster",
    "oh no",
    "don't look",
    "don't.",
    "carol, don't",
    "bushes",
    "isn't arms",
    "aren't arms",
    "lurking",
    "stalking",
    "teeth",
    "grin",
    "shhh",
    "lost boy",
    "small boy",
    "the boy",
    "that boy",
    "still out there",
    "missing kids",
    "smile didn't",
    "wrong coat",
    "between the pines",
)


def segment_is_horror_snap(text: str) -> bool:
    """True when transcript line should use the horror Recraft style (not comedy)."""
    scene = text.strip().lower()
    return any(w in scene for w in COMEDY_HORROR_SCARY_KEYWORDS)


LOST_BOY_CHARACTER = (
    "Lost Boy: small child 8-10 years old, vintage 1970s coat that looks too clean for the woods, "
    "pale face, too-wide grin, faint glowing eyes, charcoal horror illustration"
)

# Shot types for Lost Boy series — each gets its own composition prompt (not one repeated still).
LOST_BOY_SHOT_HIKERS = "hikers"
LOST_BOY_SHOT_REVEAL = "boy_reveal"
LOST_BOY_SHOT_STANDING = "boy_standing"
LOST_BOY_SHOT_WAVE = "boy_waving_group"
LOST_BOY_SHOT_DONT = "group_tension"
LOST_BOY_SHOT_CLOSEUP = "boy_closeup"
LOST_BOY_SHOT_LURKING = "boy_lurking"


def is_lost_boy_topic(topic: str) -> bool:
    return "lost boy" in (topic or "").strip().lower()


def classify_lost_boy_shot(scene: str) -> str:
    """Map transcript line → shot type so prompts change form/pose/composition."""
    s = scene.strip().lower()
    if any(x in s for x in ("he waved", "carol waved", "wave back")):
        return LOST_BOY_SHOT_WAVE
    if "carol, don't" in s or "carol don't" in s:
        return LOST_BOY_SHOT_DONT
    if "smile didn't" in s or "smile did not" in s:
        return LOST_BOY_SHOT_CLOSEUP
    if "still out there" in s or "missing kids" in s:
        return LOST_BOY_SHOT_LURKING
    if "between the pines" in s or "small boy" in s:
        return LOST_BOY_SHOT_REVEAL
    if "standing there" in s or "wrong coat" in s:
        return LOST_BOY_SHOT_STANDING
    if segment_is_horror_snap(s):
        return LOST_BOY_SHOT_STANDING
    return LOST_BOY_SHOT_HIKERS


def lost_boy_shot_prompt(shot: str, scene: str, *, beat_line: str = "") -> tuple[str, str]:
    """Return (prompt, style_lane) where style_lane is comedy | horror_solo | horror_group."""
    beat = beat_line
    if shot == LOST_BOY_SHOT_HIKERS:
        return (
            f"Hand-drawn illustration: {scene}. {beat}"
            "Two adult hikers on a sunny pine ridge trail — Carol (woman) and narrator (man). "
            "No lost child visible yet. Slightly disturbed uncanny cartoon faces, goofy morning vibe. "
            "Wide shot, forest path, birds, peaceful.",
            "comedy",
        )
    if shot == LOST_BOY_SHOT_REVEAL:
        return (
            f"Hand-drawn horror illustration: {scene}. {beat}"
            "WIDE ESTABLISHING SHOT. Two small hikers far back on the trail. "
            f"CENTER FRAME between dark pine trunks: {LOST_BOY_CHARACTER} — full body visible, "
            "standing still, first sighting, NOT a portrait close-up, NOT waving yet.",
            "horror_solo",
        )
    if shot == LOST_BOY_SHOT_STANDING:
        return (
            f"Hand-drawn horror illustration: {scene}. {beat}"
            f"MEDIUM SHOT of {LOST_BOY_CHARACTER} alone between pine trees. "
            "Wrong vintage coat detail visible. Standing stiff, arms at sides, unsettling grin. "
            "Different pose from wave or close-up shots.",
            "horror_solo",
        )
    if shot == LOST_BOY_SHOT_WAVE:
        return (
            f"Hand-drawn illustration: {scene}. {beat}"
            "THREE CHARACTERS IN ONE FRAME — pine forest trail. "
            "Foreground: two adult hikers (Carol and narrator). "
            f"Mid-background between trees: {LOST_BOY_CHARACTER} with ONE ARM RAISED waving at them. "
            "Carol waving back toward the boy. Boy must be visibly mid-wave, arm up. "
            "All three characters distinct and separate.",
            "comedy",
        )
    if shot == LOST_BOY_SHOT_DONT:
        return (
            f"Hand-drawn illustration: {scene}. {beat}"
            "THREE CHARACTERS — narrator grabbing Carol's arm, Carol still facing the boy, "
            f"Lost Boy in background between pines frozen mid-wave with wrong grin. "
            f"{LOST_BOY_CHARACTER}. Tension, don't-wave-back moment.",
            "comedy",
        )
    if shot == LOST_BOY_SHOT_CLOSEUP:
        return (
            f"Hand-drawn horror illustration: {scene}. {beat}"
            f"EXTREME CLOSE-UP of {LOST_BOY_CHARACTER} face only — frozen smile that does not move, "
            "glowing eyes, no hikers in frame, different framing from wide shots.",
            "horror_solo",
        )
    if shot == LOST_BOY_SHOT_LURKING:
        return (
            f"Hand-drawn horror illustration: {scene}. {beat}"
            f"WIDE DUSK SHOT — empty trail except {LOST_BOY_CHARACTER} far down the path "
            "watching camera, small silhouette between trees, still there, different form than close-up.",
            "horror_solo",
        )
    return (
        f"Hand-drawn illustration: {scene}. {beat} Pine forest. {LOST_BOY_CHARACTER}.",
        "horror_solo",
    )


def recraft_style_id_for_segment_text(text: str, *, topic: str = "") -> str | None:
    """Pick comedy vs horror custom style when IMAGE_PROVIDER=recraft."""
    from shorts_bot.config import settings

    if (settings.image_provider or "").strip().lower() != "recraft":
        return None

    comedy_id = (settings.recraft_style_id or "").strip()
    horror_id = (settings.recraft_style_id_horror or comedy_id).strip()

    if is_lost_boy_topic(topic):
        shot = classify_lost_boy_shot(text)
        _, lane = lost_boy_shot_prompt(shot, text)
        if lane == "comedy":
            return comedy_id or None
        return horror_id or comedy_id or None

    if segment_is_horror_snap(text):
        return horror_id or comedy_id or None
    return comedy_id or None


@dataclass
class ImageBrief:
    start_seconds: float
    end_seconds: float
    filename_stem: str
    spoken_text: str
    prompt: str
    recraft_style_id: str | None = None


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
    """Smiling Friends / Lost Boy lane — scene-specific compositions, not one repeated still."""
    scene = seg.text.strip() or topic
    beat_line = f"Shot direction: {visual_beat}. " if visual_beat else ""

    if is_lost_boy_topic(topic):
        shot = classify_lost_boy_shot(scene)
        body, _lane = lost_boy_shot_prompt(shot, scene, beat_line=beat_line)
        return (
            f"{body} "
            f"Story: {topic}. "
            "Setting: pine forest ridge trail. "
            "vertical 9:16 still image, no text, no watermark, no photorealism."
        )

    scary = segment_is_horror_snap(scene)
    if scary:
        mood = (
            "creepy forest creature snap, wrong limbs, horror beat — "
            "unique pose for this line, not a copy of prior frames"
        )
        style_line = (
            "Style: hand-drawn horror illustration, ink charcoal scratchy lines, "
            "dark forest, high contrast, unsettling."
        )
    else:
        mood = (
            "casual hiking comedy, neighbors on a trail, bright morning — "
            "characters look slightly disturbed and off-kilter (uncanny faces) but still goofy"
        )
        style_line = (
            "Style: naive hand-drawn cartoon, thick outlines, expressive slightly-disturbed faces."
        )
    return (
        f"Hand-drawn illustration still: {scene}. "
        f"{beat_line}"
        f"Story: {topic}. "
        f"Mood: {mood}. "
        "Setting: pine forest ridge trail, cartoon trees, morning light turning cold. "
        f"{style_line} "
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
                recraft_style_id=recraft_style_id_for_segment_text(seg.text, topic=topic),
            )
        )
    return briefs
