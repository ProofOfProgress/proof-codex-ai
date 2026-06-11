"""Caption formatting + render mode (Jenny 05 safe zone).

Default: **ffmpeg** — burn ASS subtitles during MP4 render (libass typography, one source
of truth, no duplicate PNG captions).

Fallback: **frame** — PIL bar on each still (offline / no ffmpeg libass).
"""

from __future__ import annotations

from shorts_bot.config import settings
from shorts_bot.production.framing import CAPTION_MAX_LINES, CAPTION_WRAP_WIDTH


def caption_mode() -> str:
    return (settings.caption_mode or "ffmpeg").strip().lower()


def burn_captions_on_frames() -> bool:
    return caption_mode() == "frame"


def burn_captions_via_ffmpeg() -> bool:
    return caption_mode() == "ffmpeg"


def format_caption_lines(
    text: str,
    *,
    max_lines: int = CAPTION_MAX_LINES,
    max_chars: int = CAPTION_WRAP_WIDTH,
) -> list[str]:
    """Word-aware wrap with ellipsis when speech exceeds the caption box."""
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return []

    words = cleaned.split()
    lines: list[str] = []
    current: list[str] = []

    for word in words:
        candidate = " ".join([*current, word]).strip()
        if len(candidate) <= max_chars:
            current.append(word)
            continue
        if current:
            lines.append(" ".join(current))
            current = [word]
        else:
            # single long token — hard split
            lines.append(word[: max_chars - 1] + "…")
            current = []
        if len(lines) >= max_lines:
            break

    if len(lines) < max_lines and current:
        lines.append(" ".join(current))

    if len(lines) > max_lines:
        lines = lines[:max_lines]

    # Ellipsis if we dropped words
    used_words = sum(len(ln.split()) for ln in lines)
    if used_words < len(words) and lines:
        last = lines[-1]
        if not last.endswith("…"):
            if len(last) >= max_chars - 1:
                last = last[: max_chars - 2] + "…"
            else:
                last = last + "…"
            lines[-1] = last

    return lines


def caption_display_text(text: str) -> str:
    return "\n".join(format_caption_lines(text))


def escape_ass_text(text: str) -> str:
    """Escape ASS dialogue special characters."""
    t = text.replace("\\", "\\\\")
    t = t.replace("{", "\\{")
    t = t.replace("}", "\\}")
    return t.replace("\n", r"\N")


def ass_force_margin_override(*, y_offset: int = 0) -> str:
    """Per-line override — caption anchor above Shorts bottom UI (see SHORTS_ALIGNMENT.md)."""
    from shorts_bot.production.framing import ass_caption_position_tag

    return ass_caption_position_tag(y_offset=y_offset)
