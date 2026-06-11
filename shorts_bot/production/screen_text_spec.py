"""Diegetic on-screen text specs — parsed from visual beats + hook (not VO captions)."""

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
]


@dataclass(frozen=True)
class ScreenTextOverlay:
    kind: OverlayKind
    primary: str
    secondary: str = ""
    tertiary: str = ""
    time_label: str = ""
    accent: str = "#FF3B30"  # iOS alert red
    feed_state: str = ""  # phone_feed: empty | figure_closer

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


def _topic_camera_label(topic: str) -> str:
    t = topic.lower()
    if "security" in t or "camera" in t:
        return "Hallway Camera"
    if "phone" in t or "text" in t or "message" in t:
        return "Messages"
    if "mirror" in t:
        return "Bathroom Cam"
    return "Live Feed"


def infer_overlay_from_spoken(
    spoken_text: str,
    *,
    hook: str = "",
    topic: str = "",
) -> ScreenTextOverlay | None:
    """VO-first overlay map — beats can drift when beat count != segment count."""
    lower = (spoken_text or "").lower()
    if not lower.strip():
        return None
    time_lbl = extract_time_label(hook, spoken_text, topic)
    cam = _topic_camera_label(topic)

    if "flagged motion" in lower or "flag motion" in lower or "motion at" in lower:
        # Hook hallway shot — no floating HUD; diegetic UI only on phone feeds
        return None
    if "live alone" in lower and "open" not in lower:
        return None
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
    if "opening security" in lower:
        return ScreenTextOverlay(
            kind="phone_feed",
            primary="Opening Security…",
            secondary=cam,
            time_label=time_lbl,
            accent="#5AC8FA",
            feed_state="app_opening",
        )
    if "opening" in lower and "security" in lower:
        return ScreenTextOverlay(
            kind="phone_feed",
            primary="Opening Security…",
            secondary=cam,
            time_label=time_lbl,
            accent="#5AC8FA",
            feed_state="app_opening",
        )
    if "hallway was empty" in lower or (
        "glitch" in lower and ("told yourself" in lower or "empty" in lower)
    ):
        return ScreenTextOverlay(
            kind="phone_feed",
            primary=cam,
            secondary=time_lbl,
            tertiary="LIVE",
            feed_state="empty",
            accent="#8EAEFF",
        )
    if "refreshed" in lower or "figure was closer" in lower or (
        "figure" in lower and "closer" in lower
    ):
        return ScreenTextOverlay(
            kind="phone_feed",
            primary=cam,
            secondary=time_lbl,
            tertiary="MOTION",
            feed_state="figure_closer",
            accent="#8EAEFF",
        )
    if "locks" in lower or "sealed" in lower:
        return None
    if "tap" in lower and "speaker" in lower:
        return ScreenTextOverlay(
            kind="phone_feed",
            primary="Live Audio",
            secondary="Tap detected",
            time_label=time_lbl,
            accent="#FF9F0A",
            feed_state="live_audio",
        )
    if "live view" in lower or ("bed" in lower and "bottom" in lower):
        return ScreenTextOverlay(
            kind="cctv_hud",
            primary="REC",
            secondary=time_lbl,
            tertiary="BEDROOM CAM",
            accent="#8EAEFF",
        )
    if "staring into the lens" in lower:
        return ScreenTextOverlay(
            kind="cctv_hud",
            primary="REC",
            secondary=time_lbl,
            tertiary="BEDROOM CAM",
            accent="#8EAEFF",
        )
    if "smiled" in lower or "lunged" in lower:
        return None
    return None


def infer_overlay_from_beat(
    beat: str,
    *,
    hook: str = "",
    topic: str = "",
    spoken_text: str = "",
) -> ScreenTextOverlay | None:
    """Map an approved visual beat to a composited UI overlay (if any)."""
    b = (beat or "").strip()
    if not b:
        return None
    lower = b.lower()
    time_lbl = extract_time_label(b, hook, spoken_text, topic)

    spoken_lower = (spoken_text or "").lower()
    if "open the app" in spoken_lower or "opened the app" in spoken_lower:
        return ScreenTextOverlay(
            kind="phone_feed",
            primary="Opening Security…",
            secondary=_topic_camera_label(topic),
            time_label=time_lbl,
            accent="#5AC8FA",
            feed_state="app_opening",
        )

    if any(k in lower for k in ("motion detected", "motion banner", "motion alert")):
        return ScreenTextOverlay(
            kind="phone_feed",
            primary="Motion Detected",
            secondary=_topic_camera_label(topic),
            time_label=time_lbl,
            accent="#FF453A",
            feed_state="motion_banner",
        )

    if any(k in lower for k in ("refresh", "figure closer", "closer in frame", "tall figure")):
        return ScreenTextOverlay(
            kind="phone_feed",
            primary=_topic_camera_label(topic),
            secondary=time_lbl,
            tertiary="MOTION",
            feed_state="figure_closer",
            accent="#8EAEFF",
        )

    if any(k in lower for k in ("security camera hallway", "motion blur", "cctv hallway")):
        return None  # full-frame CCTV I2V — no composited HUD

    if any(k in lower for k in ("live feed", "hallway empty", "empty hallway", "empty hold")):
        return ScreenTextOverlay(
            kind="phone_feed",
            primary=_topic_camera_label(topic),
            secondary=time_lbl,
            tertiary="LIVE",
            feed_state="empty",
            accent="#8EAEFF",
        )

    if any(k in lower for k in ("timestamp", "security cam", "cctv", "night vision")):
        cam = _topic_camera_label(topic)
        return ScreenTextOverlay(
            kind="cctv_hud",
            primary="REC",
            secondary=time_lbl,
            tertiary=cam.upper(),
            accent="#8EAEFF",
        )

    if any(k in lower for k in ("message", "delivered", "text", "read receipt", "slides in")):
        body = spoken_text.strip() or "Delivered"
        if "see you" in lower or "see you" in (spoken_text or "").lower():
            body = "I can see you"
        elif "delivered" in lower:
            body = "Delivered"
        return ScreenTextOverlay(
            kind="message_bubble",
            primary=body[:48],
            secondary=time_lbl,
            accent="#34C759",
        )

    if "speaker" in lower or "tap" in lower:
        return ScreenTextOverlay(
            kind="phone_feed",
            primary="Live Audio",
            secondary="Tap detected",
            time_label=time_lbl,
            accent="#FF9F0A",
            feed_state="live_audio",
        )

    if any(k in lower for k in ("figure at bed", "bed foot", "staring into")):
        return ScreenTextOverlay(
            kind="cctv_hud",
            primary="REC",
            secondary=time_lbl,
            tertiary="BEDROOM CAM",
            accent="#8EAEFF",
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

    payload = [
        s.to_dict() if s else None for s in specs
    ]
    (Path(pack_dir) / "screen_text_overlays.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
