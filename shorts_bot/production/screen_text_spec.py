"""Diegetic on-screen text specs — CCTV HUD + alarm clock (no phone screens)."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Literal

from shorts_bot.drafts.meta import visual_beat_for_segment

OverlayKind = Literal[
    "phone_alert",
    "cctv_hud",
    "message_bubble",
    "motion_chip",
    "phone_feed",
    "alarm_clock",
]


@dataclass(frozen=True)
class ScreenTextOverlay:
    kind: OverlayKind
    primary: str
    secondary: str = ""
    tertiary: str = ""
    time_label: str = ""
    accent: str = "#FF3B30"  # iOS alert red
    feed_state: str = ""  # legacy phone_feed states (disabled by default)

    def to_dict(self) -> dict:
        return asdict(self)


_TIME_RE = re.compile(
    r"(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)",
    re.IGNORECASE,
)


def extract_time_label(*parts: str) -> str:
    for text in parts:
        if not text:
            continue
        m = _TIME_RE.search(text)
        if m:
            return m.group(1).strip().upper().replace("AM", "AM").replace("PM", "PM")
    return "3:12 AM"


def phone_screens_enabled() -> bool:
    from shorts_bot.config import settings

    return bool(settings.screen_text_phone_enabled)


def _topic_camera_label(topic: str) -> str:
    t = topic.lower()
    if "security" in t or "camera" in t or "cctv" in t or "motion" in t:
        return "HALLWAY CAM"
    if "mirror" in t:
        return "BATHROOM CAM"
    if "bed" in t or "bedroom" in t:
        return "BEDROOM CAM"
    return "LIVE CAM"


def is_cctv_topic(topic: str) -> bool:
    t = (topic or "").lower()
    return any(k in t for k in ("security", "camera", "cctv", "motion", "cam", "footage"))


def _cctv_hud(
    *,
    time_lbl: str,
    cam: str,
    tertiary: str = "",
    accent: str = "#8EAEFF",
) -> ScreenTextOverlay:
    return ScreenTextOverlay(
        kind="cctv_hud",
        primary="REC",
        secondary=time_lbl,
        tertiary=tertiary or cam,
        time_label=time_lbl,
        accent=accent,
    )


def _alarm_clock(time_lbl: str) -> ScreenTextOverlay:
    return ScreenTextOverlay(
        kind="alarm_clock",
        primary=time_lbl,
        secondary="AM",
        time_label=time_lbl,
        accent="#FF453A",
    )


def _infer_cctv_spoken(
    spoken_text: str,
    *,
    hook: str = "",
    topic: str = "",
) -> ScreenTextOverlay | None:
    """Security / CCTV drafts — fullscreen feed + alarm clock for time."""
    lower = (spoken_text or "").lower()
    if not lower.strip():
        return None
    time_lbl = extract_time_label(hook, spoken_text, topic)
    cam = _topic_camera_label(topic)

    if any(k in lower for k in ("flagged motion", "flag motion", "motion at", "3:12")):
        return _alarm_clock(time_lbl)
    if "live alone" in lower and "open" not in lower:
        return _cctv_hud(time_lbl=time_lbl, cam=cam)
    if "opened the app" in lower or "open the app" in lower:
        return _cctv_hud(time_lbl=time_lbl, cam=cam, tertiary="LIVE")
    if "hallway was empty" in lower or (
        "glitch" in lower and ("told yourself" in lower or "empty" in lower)
    ):
        return _cctv_hud(time_lbl=time_lbl, cam=cam, tertiary="LIVE")
    if "refreshed" in lower or "figure was closer" in lower or (
        "figure" in lower and "closer" in lower
    ):
        return _cctv_hud(time_lbl=time_lbl, cam=cam, tertiary="MOTION")
    if "locks" in lower or "sealed" in lower:
        return _alarm_clock(time_lbl)
    if "tap" in lower and "speaker" in lower:
        return _cctv_hud(time_lbl=time_lbl, cam="AUDIO", tertiary="TAP DETECTED", accent="#FF9F0A")
    if "live view" in lower or ("bed" in lower and "bottom" in lower):
        return _cctv_hud(time_lbl=time_lbl, cam="BEDROOM CAM", tertiary="LIVE")
    if "staring into the lens" in lower:
        return _cctv_hud(time_lbl=time_lbl, cam="BEDROOM CAM", tertiary="LIVE")
    if "smiled" in lower or "lunged" in lower:
        return None
    return None


def _infer_cctv_beat(
    beat: str,
    *,
    hook: str = "",
    topic: str = "",
    spoken_text: str = "",
) -> ScreenTextOverlay | None:
    b = (beat or "").strip()
    if not b:
        return None
    lower = b.lower()
    time_lbl = extract_time_label(b, hook, spoken_text, topic)
    cam = _topic_camera_label(topic)

    if "alarm clock" in lower or "nightstand" in lower and "clock" in lower:
        return _alarm_clock(time_lbl)
    if any(k in lower for k in ("deadbolt", "door lock", "speaker")):
        return _alarm_clock(time_lbl)
    if any(k in lower for k in ("refresh", "figure closer", "closer in frame", "tall figure", "motion")):
        return _cctv_hud(time_lbl=time_lbl, cam=cam, tertiary="MOTION")
    if any(k in lower for k in ("bed foot", "figure at bed", "staring into", "bedroom")):
        return _cctv_hud(time_lbl=time_lbl, cam="BEDROOM CAM", tertiary="LIVE")
    if any(k in lower for k in ("cctv", "night vision", "security cam", "hallway", "fullscreen")):
        return _cctv_hud(time_lbl=time_lbl, cam=cam, tertiary="LIVE")
    return None


def infer_overlay_from_spoken(
    spoken_text: str,
    *,
    hook: str = "",
    topic: str = "",
) -> ScreenTextOverlay | None:
    """VO-first overlay map — CCTV + alarm clock only (no phone screens)."""
    if is_cctv_topic(topic) or not phone_screens_enabled():
        if is_cctv_topic(topic):
            return _infer_cctv_spoken(spoken_text, hook=hook, topic=topic)
        # Non-CCTV topics without phone: time on alarm clock when mentioned
        lower = (spoken_text or "").lower()
        if not phone_screens_enabled() and _TIME_RE.search(spoken_text or hook or ""):
            return _alarm_clock(extract_time_label(hook, spoken_text, topic))
        return None

    # Legacy phone path (only when screen_text_phone_enabled=true)
    lower = (spoken_text or "").lower()
    if not lower.strip():
        return None
    time_lbl = extract_time_label(hook, spoken_text, topic)
    cam = _topic_camera_label(topic)
    if "opened the app" in lower or "open the app" in lower:
        return ScreenTextOverlay(
            kind="phone_feed",
            primary=cam,
            secondary=time_lbl,
            tertiary="LIVE",
            time_label=time_lbl,
            accent="#8EAEFF",
            feed_state="empty",
        )
    return None


def infer_overlay_from_beat(
    beat: str,
    *,
    hook: str = "",
    topic: str = "",
    spoken_text: str = "",
) -> ScreenTextOverlay | None:
    """Map visual beat to composited overlay — CCTV / alarm clock."""
    if is_cctv_topic(topic) or not phone_screens_enabled():
        if is_cctv_topic(topic):
            return _infer_cctv_beat(beat, hook=hook, topic=topic, spoken_text=spoken_text)
        lower = (beat or "").lower()
        if not phone_screens_enabled() and "alarm" in lower:
            return _alarm_clock(extract_time_label(beat, hook, spoken_text, topic))
        return None

    lower = (beat or "").lower()
    time_lbl = extract_time_label(beat, hook, spoken_text, topic)
    if any(k in lower for k in ("message", "delivered", "text")):
        return ScreenTextOverlay(
            kind="message_bubble",
            primary=spoken_text.strip()[:48] or "Delivered",
            secondary=time_lbl,
            accent="#34C759",
        )
    return None


def overlays_for_segments(
    segments: list[dict],
    *,
    visual_beats: list[str] | None,
    hook: str = "",
    topic: str = "",
) -> list[ScreenTextOverlay | None]:
    total = len(segments)
    out: list[ScreenTextOverlay | None] = []
    for i, seg in enumerate(segments):
        spoken = str(seg.get("spoken_text") or "")
        ov = infer_overlay_from_spoken(spoken, hook=hook, topic=topic)
        if ov is None:
            beat = visual_beat_for_segment(visual_beats, i, total)
            if beat:
                ov = infer_overlay_from_beat(
                    beat,
                    hook=hook,
                    topic=topic,
                    spoken_text=spoken,
                )
        out.append(ov)
    return out


def write_overlay_manifest(pack_dir, specs: list[ScreenTextOverlay | None]) -> None:
    import json
    from pathlib import Path

    payload = [s.to_dict() if s else None for s in specs]
    (Path(pack_dir) / "screen_text_overlays.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
