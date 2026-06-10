"""9:16 framing + caption safe zones (Jenny Hoyos course file 05 — silent clarity).

Jenny 05: phone-first filming, rule of thirds, keep text/visuals in the safe zone,
review on mute before upload. YouTube Shorts overlays title + buttons on the bottom
~15–20% of frame — burned-in captions must sit above that band.

Research: docs/SHORTS_ALIGNMENT.md (Poster.ly / Koro / cross-platform subtitle union).
"""

from __future__ import annotations

FRAME_WIDTH = 1080
FRAME_HEIGHT = 1920

# Platform UI — keep subject out of these bands
SHORTS_UI_TOP_PX = 120
SHORTS_UI_BOTTOM_PX = 380
SHORTS_UI_RIGHT_PX = 120
SHORTS_UI_LEFT_PX = 60

# Stick figure "camera" — subject in upper-middle, left of right rail
ACTION_ZONE_TOP_PX = 280
ACTION_ZONE_BOTTOM_PX = 1080
ACTION_CENTER_X_RATIO = 0.42

# Captions — lower-middle, above Shorts title/like rail (not flush to bottom)
CAPTION_BOTTOM_MARGIN_PX = 400
CAPTION_ANCHOR_Y_PX = FRAME_HEIGHT - CAPTION_BOTTOM_MARGIN_PX
CAPTION_SIDE_MARGIN_PX = 90
CAPTION_FONT_SIZE = 36
CAPTION_LINE_HEIGHT = 44
CAPTION_WRAP_WIDTH = 28
CAPTION_MAX_LINES = 2

# ASS subtitles (ffmpeg burn-in) — match caption band
SUBTITLE_MARGIN_V_PX = CAPTION_BOTTOM_MARGIN_PX
SUBTITLE_FONT_SIZE = 46

# Legacy alias (Jenny 05)
SAFE_ZONE_TOP_PX = SHORTS_UI_TOP_PX
SAFE_ZONE_BOTTOM_UI_PX = SHORTS_UI_BOTTOM_PX


def caption_bar_y(bar_height: int, *, frame_height: int = FRAME_HEIGHT) -> int:
    """Top Y coordinate for the PIL caption bar background."""
    return frame_height - bar_height - CAPTION_BOTTOM_MARGIN_PX


def action_figure_position(*, width: int = FRAME_WIDTH, height: int = FRAME_HEIGHT) -> tuple[int, int]:
    """Default stick-figure anchor — upper-middle, clear of right UI rail."""
    x = int(width * ACTION_CENTER_X_RATIO)
    y = int(height * 0.40)
    return x, y


def ass_caption_position_tag(*, width: int = FRAME_WIDTH, y_offset: int = 0) -> str:
    """ASS override: bottom-center anchor above Shorts UI overlay."""
    y = CAPTION_ANCHOR_Y_PX + y_offset
    return rf"{{\an2\pos({width // 2},{y})}}"


def framing_notes_for_prompt() -> str:
    """Image-prompt fragment enforcing Jenny 05 safe composition."""
    return (
        "Compose subject and action between 15% and 55% from top of vertical frame; "
        "keep right 120px and bottom 40% minimal for caption + Shorts UI safe zone. "
        "Rule of thirds, generous negative space, no text in image."
    )


def stick_framing_notes_for_prompt() -> str:
    """ChainsFR format — character acts the beat; minimal set dressing per timestamp."""
    return (
        "Stick figure ACTING the spoken line — place in upper-middle (not bottom half), "
        "slightly left of center to avoid right-side like/comment rail. "
        "MS-Paint-simple line art, off-white #F4F4F0, black outlines. "
        "Bottom 40% clear for burned captions + YouTube Shorts UI."
    )
