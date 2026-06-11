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
            kind="phone_alert",
            primary="Opening Security…",
            secondary=_topic_camera_label(topic),
            time_label=time_lbl,
            accent="#5AC8FA",
        )

    if any(k in lower for k in ("phone screen", "security app", "lock screen", "notification", "opening")):
        return ScreenTextOverlay(
            kind="phone_alert",
            primary="Motion Detected",
            secondary=_topic_camera_label(topic),
            time_label=time_lbl,
            accent="#FF453A",
        )

    if any(k in lower for k in ("refresh", "figure closer", "closer in frame", "tall figure")):
        return ScreenTextOverlay(
            kind="phone_feed",
            primary=_topic_camera_label(topic),
            secondary=time_lbl,
            tertiary="MOTION",
            feed_state="figure_closer",
            accent="#39FF14",
        )

    if any(k in lower for k in ("security camera hallway", "motion blur", "cctv hallway")):
        return ScreenTextOverlay(
            kind="cctv_hud",
            primary="REC",
            secondary=time_lbl,
            tertiary="MOTION",
            accent="#39FF14",
        )

    if any(k in lower for k in ("live feed", "hallway empty", "empty hallway", "empty hold")):
        return ScreenTextOverlay(
            kind="phone_feed",
            primary=_topic_camera_label(topic),
            secondary=time_lbl,
            tertiary="LIVE",
            feed_state="empty",
            accent="#39FF14",
        )

    if any(k in lower for k in ("timestamp", "security cam", "cctv", "night vision")):
        cam = _topic_camera_label(topic)
        return ScreenTextOverlay(
            kind="cctv_hud",
            primary="REC",
            secondary=time_lbl,
            tertiary=cam.upper(),
            accent="#39FF14",
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
            kind="phone_alert",
            primary="Live Audio",
            secondary="Tap detected",
            time_label=time_lbl,
            accent="#FF9F0A",
        )

    if any(k in lower for k in ("figure at bed", "bed foot", "staring into")):
        return ScreenTextOverlay(
            kind="cctv_hud",
            primary="REC",
            secondary=time_lbl,
            tertiary="BEDROOM CAM",
            accent="#39FF14",
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
        beat = visual_beat_for_segment(visual_beats, i, total)
        if not beat:
            out.append(None)
            continue
        spoken = str(seg.get("spoken_text") or "")
        out.append(
            infer_overlay_from_beat(
                beat,
                hook=hook,
                topic=topic,
                spoken_text=spoken,
            )
        )
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
