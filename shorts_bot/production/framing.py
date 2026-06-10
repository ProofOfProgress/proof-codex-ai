"""9:16 framing + caption safe zones (Jenny Hoyos course file 05 — silent clarity).

Jenny 05: phone-first filming, rule of thirds, keep text/visuals in the safe zone,
review on mute before upload. YouTube Shorts overlays title + buttons on the bottom
~15–18% of frame — burned-in captions must sit above that band.
"""

from __future__ import annotations

FRAME_WIDTH = 1080
FRAME_HEIGHT = 1920

# Jenny 05 + Shorts UI: subject/action in upper ~62% of frame
SAFE_ZONE_TOP_PX = 120
SAFE_ZONE_BOTTOM_UI_PX = 340  # YouTube title, like, comment, progress bar

# Caption bar sits above the Shorts UI overlay (not flush to bottom)
CAPTION_BOTTOM_MARGIN_PX = 320
CAPTION_SIDE_MARGIN_PX = 40
CAPTION_FONT_SIZE = 36
CAPTION_LINE_HEIGHT = 44
CAPTION_WRAP_WIDTH = 28
CAPTION_MAX_LINES = 2

# ASS subtitles (optional burn-in / SRT companion) — match caption band
SUBTITLE_MARGIN_V_PX = 320
SUBTITLE_FONT_SIZE = 52


def caption_bar_y(bar_height: int, *, frame_height: int = FRAME_HEIGHT) -> int:
    """Top Y coordinate for the caption bar background."""
    return frame_height - bar_height - CAPTION_BOTTOM_MARGIN_PX


def framing_notes_for_prompt() -> str:
    """Image-prompt fragment enforcing Jenny 05 safe composition."""
    return (
        "Compose subject and action in the upper 60% of the vertical frame; "
        "keep bottom 18% empty/minimal for caption safe zone (Jenny 05 framing). "
        "Rule of thirds, generous negative space, no text in image."
    )


def stick_framing_notes_for_prompt() -> str:
    """ChainsFR couch format — character + couch in mid-frame, props in background."""
    return (
        "Fixed couch in lower-mid frame; stick figure sitting or standing beside it acting the line. "
        "Background props change per timestamp (window, lamp, door, plant) but couch stays identical. "
        "MS-Paint-simple line art, off-white wall #E8E5DE, black stick figure. "
        "Bottom 18% clear for caption safe zone (Jenny 05)."
    )
