"""AI video prompt builder — Soft Continuity VISUAL DNA + 5-part clip framework.

See docs/AI_VIDEO_PROMPTING_RESEARCH.md for model tuning and hybrid stack guidance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from shorts_bot.production.framing import framing_notes_for_prompt
from shorts_bot.production.stick_background import plan_room
from shorts_bot.production.turboscribe_parser import TranscriptSegment

ModelHint = Literal["kling", "runway", "veo", "pika", "luma", "hailuo", "auto"]


@dataclass(frozen=True)
class VideoTemplate:
    """Production template — one cosy beat, one visible action."""

    id: str
    name: str
    keywords: tuple[str, ...]
    subject: str
    action: str
    camera: str
    environment: str
    style: str
    end_state: str
    duration_seconds: float = 4.0
    model_hint: ModelHint = "auto"
    role: Literal["hook", "problem", "protocol", "payoff"] = "protocol"


@dataclass
class VideoPromptBrief:
    start_seconds: float
    end_seconds: float
    filename_stem: str
    spoken_text: str
    prompt: str
    negative_prompt: str
    template_id: str
    end_state: str
    model_hint: ModelHint
    duration_seconds: float


def visual_dna() -> str:
    """Paste unchanged into every clip prompt."""
    return (
        "VISUAL DNA — Soft Continuity: "
        "Style: polished minimal illustration, soft film grain, not photoreal, not 3D, not anime. "
        "Palette: cream #F5EFE6, floor #E8DFD4, sage #9DB8A0, terracotta #C9A08A, lamp #F2D98A, rain #A8B8C8. "
        "Lighting: warm floor lamp key, soft shadows, no fluorescent. "
        "Composition: 9:16; action upper 55%; bottom 40% empty for captions + Shorts UI. "
        "Faceless: hands, silhouettes from behind, POV only — no faces. "
        "Motion: slow push-in or static; meditative, not TikTok frantic."
    )


def negative_block() -> str:
    return (
        "no faces, no text, no watermark, no logos, morphing textures, camera shake, "
        "extra fingers, horror, office fluorescent, photoreal skin, 3D render, anime"
    )


def templates() -> list[VideoTemplate]:
    """Ten production templates — cosy mental-health Short beats."""
    return [
        VideoTemplate(
            id="sunday_couch_phone",
            name="Sunday couch phone hook",
            keywords=("sunday", "couch", "phone", "scroll", "check your phone"),
            subject="Faceless silhouette on terracotta couch, phone glowing in lap",
            action="Thumb hovers over lock screen, shoulders slightly hunched, rain on window",
            camera="Medium static, locked tripod, slight vignette",
            environment="Cream wall, rain-streaked window, sage throw, warm floor lamp glow",
            style="Minimal illustration, soft grain, meditative Sunday dread",
            end_state="Thumb still hovering, phone glow unchanged, rain visible",
            duration_seconds=3.0,
            model_hint="runway",
            role="hook",
        ),
        VideoTemplate(
            id="timer_not_scroll",
            name="Timer instead of scroll",
            keywords=("timer", "scroll", "five minute", "5 minute", "instead of"),
            subject="POV hands holding phone beside small kitchen timer",
            action="Finger taps timer app start; phone screen dims as timer counts",
            camera="Close medium static, hands in upper frame",
            environment="Cosy kitchen nook, cream counter, mug edge in frame, lamp warmth",
            style="Clean minimal illustration, one prop focus",
            end_state="Timer digits visible, phone face-down beside it",
            duration_seconds=4.0,
            model_hint="pika",
            role="protocol",
        ),
        VideoTemplate(
            id="three_breaths",
            name="Three breaths grounding",
            keywords=("breath", "breathe", "inhale", "exhale", "ground"),
            subject="Silhouette seated by floor lamp, blanket on shoulders",
            action="Shoulders rise on inhale, fall on exhale — three slow cycles",
            camera="Slow 10% push-in over 4s, locked after beat one",
            environment="Calm lamp key light, cream wall, sage plant silhouette",
            style="Meditative, soft shadows, minimal motion",
            end_state="Shoulders at rest, lamp glow steady",
            duration_seconds=5.0,
            model_hint="kling",
            role="protocol",
        ),
        VideoTemplate(
            id="bed_3am",
            name="3am bed insomnia",
            keywords=("3am", "3 am", "can't sleep", "cant sleep", "insomnia", "wake"),
            subject="Face-down on pillow POV, phone dark on nightstand",
            action="Fingers curl blanket edge; subtle chest rise, no phone reach",
            camera="Low static bedside angle, locked tripod",
            environment="Soft night window #2A3040, dim lamp, cream bedding",
            style="Quiet night illustration, not horror, adult loneliness",
            end_state="Phone untouched, blanket held, breathing slowed",
            duration_seconds=4.0,
            model_hint="luma",
            role="problem",
        ),
        VideoTemplate(
            id="rainy_overthinking",
            name="Rainy window overthinking",
            keywords=("rain", "overthink", "grey", "window", "storm"),
            subject="Silhouette at rain-streaked window, arms wrapped",
            action="Raindrops slide; figure still, slight head tilt down",
            camera="Medium static, window fills upper half",
            environment="Rain glass #A8B8C8, cream room, terracotta couch edge",
            style="Grey-day cosy, soft grain, contemplative",
            end_state="Same pose, one new rain streak path",
            duration_seconds=5.0,
            model_hint="runway",
            role="problem",
        ),
        VideoTemplate(
            id="dreaded_text",
            name="Before dreaded text reply",
            keywords=("message", "text", "reply", "dreading", "open a message"),
            subject="Hands on phone, notification banner blurred, on couch",
            action="Thumb circles send button without pressing; hesitation loop",
            camera="Close-up hands, locked, upper 50% of frame",
            environment="Terracotta couch, throw, warm lamp, cream wall",
            style="Tension without faces, minimal illustration",
            end_state="Thumb lifted off screen, phone lowered slightly",
            duration_seconds=4.0,
            model_hint="kling",
            role="hook",
        ),
        VideoTemplate(
            id="door_party",
            name="Door before party",
            keywords=("party", "door", "walk in", "alone", "crowd"),
            subject="Back-view silhouette at apartment door, coat on",
            action="Hand on doorknob, frozen; shallow breath visible in shoulders",
            camera="Medium static from behind, door centered upper frame",
            environment="Warm hallway lamp, cream walls, muted coat terracotta",
            style="Social anxiety beat, soft not dramatic",
            end_state="Hand still on knob, door unopened",
            duration_seconds=3.5,
            model_hint="veo",
            role="hook",
        ),
        VideoTemplate(
            id="shame_spiral_couch",
            name="Shame spiral couch huddle",
            keywords=("shame", "spiral", "huddle", "can't move", "cant move", "couch"),
            subject="Curled silhouette on couch under throw, knees up",
            action="Minimal rock forward then still; phone face-down on cushion",
            camera="Wide medium static, figure left of center",
            environment="Cosy couch, rain window, lamp glow, cream palette",
            style="Low-spoon depression beat, gentle not melodramatic",
            end_state="Figure slightly less curled, phone still down",
            duration_seconds=4.5,
            model_hint="kling",
            role="problem",
        ),
        VideoTemplate(
            id="mug_micro_win",
            name="Low-spoon mug micro-win",
            keywords=("mug", "tea", "micro-win", "one thing", "warm drink"),
            subject="Hands wrapping terracotta mug, steam rising",
            action="Steam curls upward; hands lift mug one inch, not drinking yet",
            camera="Close static, mug centered upper third",
            environment="Kitchen nook, cream counter, sage plant blur",
            style="Small win ritual, warm and achievable",
            end_state="Steam steady, mug held at chest height",
            duration_seconds=3.5,
            model_hint="pika",
            role="protocol",
        ),
        VideoTemplate(
            id="payoff_lamp_still",
            name="Payoff ring / lamp stillness",
            keywords=("still here", "payoff", "minute", "ring", "lamp", "done"),
            subject="Empty couch with warm lamp and faint thin ring on cushion",
            action="Lamp flicker settles; room perfectly still, no figure",
            camera="Slow 5% push-in to lamp, locked end",
            environment="Cream wall, terracotta couch, sage throw folded",
            style="Resolution stillness, CTA space in bottom 40%",
            end_state="Lamp glow steady, ring faint, room calm",
            duration_seconds=4.0,
            model_hint="runway",
            role="payoff",
        ),
    ]


def _score_template(template: VideoTemplate, text: str) -> int:
    lower = text.lower()
    return sum(1 for kw in template.keywords if kw in lower)


def match_template(*, topic: str, spoken_text: str = "") -> VideoTemplate:
    """Pick best template for topic + segment line."""
    combined = f"{topic} {spoken_text}".strip()
    scored = [(t, _score_template(t, combined)) for t in templates()]
    scored.sort(key=lambda x: (-x[1], x[0].id))
    if scored[0][1] > 0:
        return scored[0][0]

    room = plan_room(spoken_text or topic)
    bg = room.background.value.replace("_", " ")
    return VideoTemplate(
        id="derived",
        name=f"Derived — {bg}",
        keywords=(),
        subject=f"Faceless figure or hands in {bg} setting",
        action=f"One slow motion illustrating: {spoken_text or topic}",
        camera="Medium static, locked tripod or slow 10% push-in",
        environment=f"Cosy {bg}, cream #F5EFE6, warm lamp, props: {', '.join(room.wall_props) or 'minimal'}",
        style="Minimal illustration, soft grain, meditative",
        end_state="Pose held, environment unchanged",
        duration_seconds=4.0,
        model_hint="auto",
        role="protocol",
    )


def _model_suffix(hint: ModelHint) -> str:
    hints = {
        "kling": "Optimize for Kling 3: rich physics verbs, one coherent motion arc.",
        "runway": "Optimize for Runway Gen-4: mood-first, cinematic atmosphere.",
        "veo": "Optimize for Veo 3.1: concise motion-forward, photoreal-adjacent still restrained.",
        "pika": "Optimize for Pika: short stylized clip, minimal style keyword.",
        "luma": "Optimize for Luma Dream Machine: natural flowing sentence rhythm.",
        "hailuo": "Optimize for Minimax Hailuo: narrative sentence, not keyword list.",
        "auto": "Route: hook→Runway/Kling, protocol→Pika/Luma, payoff→Runway.",
    }
    return hints.get(hint, hints["auto"])


def segment_to_video_prompt(
    seg: TranscriptSegment,
    *,
    topic: str,
    template: VideoTemplate | None = None,
    continuity_in: str | None = None,
    clip_index: int = 0,
) -> str:
    """Build one I2V/T2V clip prompt using the 5-part framework."""
    tmpl = template or match_template(topic=topic, spoken_text=seg.text)
    scene_line = seg.text.strip() or topic
    continuity = ""
    if continuity_in:
        continuity = f"CONTINUITY IN: {continuity_in}. "

    parts = [
        visual_dna(),
        continuity,
        f"SUBJECT: {tmpl.subject}. ",
        f"ACTION: {tmpl.action} — beat: {scene_line}. ",
        f"CAMERA: {tmpl.camera}. {framing_notes_for_prompt()} ",
        f"ENVIRONMENT: {tmpl.environment}. ",
        f"STYLE: {tmpl.style}. ",
        f"END STATE: {tmpl.end_state}. ",
        f"Clip {clip_index + 1}, target {tmpl.duration_seconds:.0f}s, 9:16 vertical video. ",
        _model_suffix(tmpl.model_hint),
    ]
    return "".join(parts)


def build_video_prompt_briefs(
    segments: list[TranscriptSegment],
    *,
    topic: str,
    total_duration: float | None = None,
) -> list[VideoPromptBrief]:
    """One video prompt per AV segment, with END STATE → CONTINUITY IN chaining."""
    if not segments:
        return []

    from shorts_bot.production.turboscribe_parser import label_from_seconds

    briefs: list[VideoPromptBrief] = []
    prev_end_state: str | None = None

    for i, seg in enumerate(segments):
        if i + 1 < len(segments):
            end = segments[i + 1].start_seconds
        elif total_duration and total_duration > seg.start_seconds:
            end = total_duration
        else:
            end = seg.start_seconds + 5.0

        tmpl = match_template(topic=topic, spoken_text=seg.text)
        prompt = segment_to_video_prompt(
            seg,
            topic=topic,
            template=tmpl,
            continuity_in=prev_end_state,
            clip_index=i,
        )
        stem = label_from_seconds(seg.start_seconds)
        duration = min(max(end - seg.start_seconds, 2.5), 8.0)

        briefs.append(
            VideoPromptBrief(
                start_seconds=seg.start_seconds,
                end_seconds=end,
                filename_stem=stem,
                spoken_text=seg.text,
                prompt=prompt,
                negative_prompt=negative_block(),
                template_id=tmpl.id,
                end_state=tmpl.end_state,
                model_hint=tmpl.model_hint,
                duration_seconds=duration,
            )
        )
        prev_end_state = tmpl.end_state

    return briefs
