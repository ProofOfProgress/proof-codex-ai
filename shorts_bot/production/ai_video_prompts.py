"""AI video prompt builder — Don't Blink horror VISUAL DNA + 5-part clip framework.

See docs/AI_VIDEO_PROMPTING_RESEARCH.md for model tuning and hybrid stack guidance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from shorts_bot.production.framing import framing_notes_for_prompt, screen_text_prompt_note
from shorts_bot.production.turboscribe_parser import TranscriptSegment
from shorts_bot.production.horror_lane import analog_color_rules, horror_lane_compact
from shorts_bot.production.world import world_visual_continuity

ModelHint = Literal["kling", "runway", "veo", "pika", "luma", "hailuo", "auto"]


@dataclass(frozen=True)
class VideoTemplate:
    """Production template — one horror beat, one visible wrongness."""

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
    role: Literal["hook", "escalation", "false_calm", "jumpscare"] = "escalation"


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
        "VISUAL DNA — Don't Blink horror: "
        "Style: cinematic photoreal horror still, film grain, harsh contrast, underexposed — not illustration, not anime. "
        "Palette: black #0A0A0A, cold blue #1A2A3A, deep crimson #8B0000 accents, sickly green sparingly. "
        "Lighting: single harsh source or security-cam IR, deep shadows, no warm lamp glow. "
        "Composition: 9:16 vertical; subject upper 55%; bottom 40% empty for captions + Shorts UI. "
        "Faceless until scare beat: silhouettes, CCTV POV, hallway depth — no phones, no identifiable faces until final lunge. "
        "Motion: slow dread drift or locked static; final beat may snap fast toward camera. "
        f"{world_visual_continuity()} "
        f"{analog_color_rules()} "
        f"{horror_lane_compact()}"
    )


def negative_block() -> str:
    return (
        "no text, no watermark, no logos, no stick figures, no cosy aesthetic, no cream palette, "
        "no warm lamp, no couch tea ritual, no self-help illustration, no anime, no bright daylight, "
        "morphing textures, extra fingers, gore, blood spray, office fluorescent, cheerful mood"
    )


def templates() -> list[VideoTemplate]:
    """Ten production templates — Don't Blink horror Short beats."""
    return [
        VideoTemplate(
            id="mirror_blink",
            name="Mirror delayed blink",
            keywords=("mirror", "reflection", "blink", "blinked", "glass"),
            subject="Bathroom mirror POV, your dark silhouette facing fogged glass",
            action="You blink — reflection blinks one second late; eyes stay open when yours close",
            camera="Medium static mirror POV, locked tripod, slight handheld micro-jitter on scare",
            environment="Cold blue tile, black grout, underexposed vanity bulb flicker",
            style="Uncanny reflection horror, photoreal, film grain, terrifying wrongness",
            end_state="Reflection frozen mid-blink while real figure moves",
            duration_seconds=4.0,
            model_hint="runway",
            role="hook",
        ),
        VideoTemplate(
            id="security_cam_motion",
            name="Security cam motion alone",
            keywords=("security", "camera", "motion", "alone", "flagged", "cctv"),
            subject="Grainy security cam overlay, empty living room night vision green",
            action="Motion box appears in corner — nothing visible until box pulses once",
            camera="Fixed high-corner CCTV angle, timestamp burn feel without readable text",
            environment="Dark apartment, cold blue-black, furniture silhouettes",
            style="Found-footage surveillance horror, low-res grain, dread",
            end_state="Motion box locked on empty doorway",
            duration_seconds=3.5,
            model_hint="veo",
            role="hook",
        ),
        VideoTemplate(
            id="wrong_text_delivered",
            name="Text delivered phone off",
            keywords=("text", "message", "delivered", "phone", "notification", "read"),
            subject="Phone screen close-up, message thread, face-down body in bed blur",
            action="Delivered checkmark appears — phone was powered off; screen glows alone",
            camera="Close macro on phone, shallow depth, upper 50% frame",
            environment="Black bedroom, cold screen light on sheets, no warm tones",
            style="Digital uncanny horror, photoreal phone UI shape without readable text",
            end_state="Screen lit, room still dark, no hands on device",
            duration_seconds=3.5,
            model_hint="kling",
            role="hook",
        ),
        VideoTemplate(
            id="knock_inside_closet",
            name="Knock from inside closet",
            keywords=("knock", "closet", "inside", "door", "wardrobe"),
            subject="Closed closet door in narrow hallway, scratch marks on inside edge",
            action="Door shudders once from within; handle does not move",
            camera="Slow push-in down hallway toward door, low angle",
            environment="Black hallway #0A0A0A, cold blue spill, deep shadow under door",
            style="Domestic invasion dread, photoreal, silence before hit",
            end_state="Door still, fresh scratch visible on inside jamb",
            duration_seconds=4.5,
            model_hint="luma",
            role="escalation",
        ),
        VideoTemplate(
            id="hallway_longer",
            name="Hallway longer than yesterday",
            keywords=("hallway", "longer", "stairs", "corridor", "steps"),
            subject="Impossibly long apartment hallway, doors repeating into darkness",
            action="Slow drift forward — end wall keeps receding, one new door appears",
            camera="Steadicam drift forward, centered vanishing point",
            environment="Liminal interior, cold blue walls, single buzzing fluorescent far away",
            style="Spatial wrongness horror, Kubrick symmetry, terrifying",
            end_state="Hallway longer than frame can hold, dark end unresolved",
            duration_seconds=5.0,
            model_hint="runway",
            role="escalation",
        ),
        VideoTemplate(
            id="photo_corner_figure",
            name="Photo someone in corner",
            keywords=("photo", "picture", "corner", "camera roll", "flash"),
            subject="Phone gallery photo of your own room at night, wide angle",
            action="Zoom into corner — faint tall silhouette not there when photo was taken",
            camera="Screen-in-screen zoom, handheld micro shake",
            environment="Dark room in photo, cold blue window spill, grain heavy",
            style="Paranormal evidence horror, photoreal, subtle figure",
            end_state="Silhouette sharper on pinch-zoom, room otherwise empty",
            duration_seconds=4.0,
            model_hint="pika",
            role="escalation",
        ),
        VideoTemplate(
            id="muted_call_breath",
            name="Muted call breathing",
            keywords=("muted", "call", "breathing", "phone", "silence"),
            subject="Phone call UI dark mode, mute icon implied, ear POV dark room",
            action="Waveform flat while slow breath audio implied visually via fog on glass",
            camera="Close on phone + ear silhouette edge",
            environment="Black room, phone screen only light, cold blue",
            style="Audio-as-horror, claustrophobic, photoreal",
            end_state="Breath rhythm visible as condensation pulse on window",
            duration_seconds=4.0,
            model_hint="hailuo",
            role="escalation",
        ),
        VideoTemplate(
            id="false_calm_static",
            name="False calm hold",
            keywords=("quiet", "still", "maybe", "nothing", "lag", "trick", "told yourself"),
            subject="Same room as prior beat — now perfectly still, empty center frame",
            action="Almost no motion — slow blink of light, hold tension, bait safety",
            camera="Locked static wide, security-cam stillness",
            environment="Underexposed interior, cold blue, deep black corners",
            style="Hitchcock silence beat, dread without motion, photoreal",
            end_state="Frame frozen calm, shadow unchanged",
            duration_seconds=5.0,
            model_hint="runway",
            role="false_calm",
        ),
        VideoTemplate(
            id="suspense_replay_hold",
            name="Suspense into replay",
            keywords=("watch", "again", "wait", "freeze", "staring", "hold", "replay"),
            subject="Same dread frame as prior beat — wrong detail barely visible, no lunge",
            action="Locked hold, micro shadow drift, tension peaks then hard stop — no scare payoff",
            camera="Slow 2% zoom out, static dread, 9:16 — cut invites Shorts replay",
            environment="Black crush, cold blue, film grain, underexposed",
            style="Unresolved horror, replay bait, photoreal, no jumpscare",
            end_state="Frame holds on wrong detail — viewer replays to catch it",
            duration_seconds=5.0,
            model_hint="runway",
            role="false_calm",
        ),
        VideoTemplate(
            id="face_unlock_wrong",
            name="Face unlock without looking",
            keywords=("face unlock", "unlock", "looking", "screen", "selfie"),
            subject="Phone lock screen POV, face ID scan animation implied",
            action="Phone unlocks while you look away — screen shows your face staring back",
            camera="POV phone in hand, tilt down to screen",
            environment="Dark hallway reflection in glass, cold blue UI glow",
            style="Digital possession horror, terrifying close-up",
            end_state="Screen shows face you are not making",
            duration_seconds=3.5,
            model_hint="kling",
            role="escalation",
        ),
        VideoTemplate(
            id="jumpscare_tease",
            name="Fake scare tease",
            keywords=("shudder", "flinch", "almost", "something moved", "flicker"),
            subject="Dark hallway or mirror edge — shape barely visible",
            action="Brief snap toward camera then freeze — false scare, not full lunge",
            camera="Quick 0.5s push-in then hard stop, 9:16",
            environment="Black crush, cold blue, grain",
            style="Decoy scare tease, photoreal horror",
            end_state="Frame holds on empty space — bait for real scare later",
            duration_seconds=2.5,
            model_hint="hailuo",
            role="escalation",
        ),
        VideoTemplate(
            id="jumpscare_lunge",
            name="Final jumpscare lunge",
            keywords=(
                "lunged",
                "scream",
                "opened",
                "behind you",
                "turned",
                "closet",
                "mirror",
                "grab",
                "face",
                "jumpscare",
                "payoff",
            ),
            subject="Full-frame horror face or figure rushing from mirror/door/darkness",
            action="Sudden fast lunge toward camera, motion blur, mouth open, eyes wide",
            camera="Snap zoom or rapid dolly in, 9:16 full bleed scare",
            environment="Black crush shadows, crimson accent, harsh flash",
            style="Earned jumpscare, maximum terror, photoreal, not gore",
            end_state="Face fills frame, motion peaked, cut on impact",
            duration_seconds=3.0,
            model_hint="hailuo",
            role="jumpscare",
        ),
    ]


def _score_template(template: VideoTemplate, text: str) -> int:
    lower = text.lower()
    return sum(1 for kw in template.keywords if kw in lower)


def match_template(
    *,
    topic: str,
    spoken_text: str = "",
    segment_index: int | None = None,
) -> VideoTemplate:
    """Pick best template for topic + segment line."""
    combined = f"{topic} {spoken_text}".strip()
    pool = templates()
    if segment_index == 0:
        hooks = [t for t in pool if t.role == "hook"]
        if hooks:
            pool = hooks
    scored = [(t, _score_template(t, combined)) for t in pool]
    scored.sort(key=lambda x: (-x[1], x[0].id))
    if scored[0][1] > 0:
        return scored[0][0]

    scene = (spoken_text or topic).strip()[:80]
    return VideoTemplate(
        id="derived_horror",
        name=f"Derived horror — {scene[:40]}",
        keywords=(),
        subject="Dark hallway, mirror, fullscreen CCTV, or closet — faceless POV, no phones",
        action=f"Slow uncanny motion then wrong detail: {scene}",
        camera="Slow push-in or locked static, horror framing, 9:16",
        environment="Black and cold blue, film grain, liminal empty room",
        style="Cinematic horror, terrifying, photorealistic, no cosy palette",
        end_state="Shadow shifts or reflection wrong",
        duration_seconds=4.0,
        model_hint="auto",
        role="escalation",
    )


def _model_suffix(hint: ModelHint) -> str:
    hints = {
        "kling": "Optimize for Kling 3: rich physics verbs, one coherent motion arc.",
        "runway": "Optimize for Runway Gen-4: mood-first, cinematic atmosphere.",
        "veo": "Optimize for Veo 3.1: concise motion-forward, photoreal horror.",
        "pika": "Optimize for Pika: short stylized clip, minimal style keyword.",
        "luma": "Optimize for Luma Dream Machine: natural flowing sentence rhythm.",
        "hailuo": "Optimize for Minimax Hailuo: narrative sentence, lunge on scare beats.",
        "auto": "Route: hook→Runway/Veo, escalation→Kling/Luma, false calm→Runway static, jumpscare→Hailuo.",
    }
    return hints.get(hint, hints["auto"])


def segment_to_video_prompt(
    seg: TranscriptSegment,
    *,
    topic: str,
    template: VideoTemplate | None = None,
    continuity_in: str | None = None,
    clip_index: int = 0,
    visual_beat: str | None = None,
) -> str:
    """Build one I2V/T2V clip prompt using the 5-part framework."""
    tmpl = template or match_template(
        topic=topic, spoken_text=seg.text, segment_index=clip_index
    )
    scene_line = seg.text.strip() or topic
    continuity = ""
    if continuity_in:
        continuity = f"CONTINUITY IN: {continuity_in}. "
    shot_dir = ""
    if visual_beat:
        shot_dir = f"SHOT DIRECTION (approved beat): {visual_beat}. "

    parts = [
        visual_dna(),
        continuity,
        shot_dir,
        f"SUBJECT: {tmpl.subject}. ",
        f"ACTION: {tmpl.action} — beat: {scene_line}. ",
        f"CAMERA: {tmpl.camera}. {framing_notes_for_prompt()} {screen_text_prompt_note()} ",
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
    visual_beats: list[str] | None = None,
    jumpscare_plan=None,
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

        tmpl = match_template(topic=topic, spoken_text=seg.text, segment_index=i)
        if jumpscare_plan is not None:
            primary = int(jumpscare_plan.primary_segment_index)
            profile = getattr(jumpscare_plan, "profile", "finale")
            has_js = getattr(jumpscare_plan, "has_jumpscare", profile != "suspense_replay")
            lunge = next((t for t in templates() if t.id == "jumpscare_lunge"), None)
            replay_hold = next((t for t in templates() if t.id == "suspense_replay_hold"), None)
            if profile == "suspense_replay" and i == len(segments) - 1 and replay_hold:
                tmpl = replay_hold
            elif has_js and i == primary and lunge:
                tmpl = lunge
        elif i == len(segments) - 1 and tmpl.role != "jumpscare":
            jumpscare = next((t for t in templates() if t.id == "jumpscare_lunge"), None)
            if jumpscare:
                tmpl = jumpscare

        from shorts_bot.drafts.meta import visual_beat_for_segment

        beat_hint = visual_beat_for_segment(visual_beats, i, len(segments))
        prompt = segment_to_video_prompt(
            seg,
            topic=topic,
            template=tmpl,
            continuity_in=prev_end_state,
            clip_index=i,
            visual_beat=beat_hint,
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
