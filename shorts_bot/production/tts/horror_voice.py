"""Horror niche TTS delivery — dread pacing without monotone, Shorts-length (~30s)."""

from __future__ import annotations

import re

FALSE_CALM_RE = re.compile(
    r"\b(told yourself|maybe it was|just tired|nothing moved|for a second|held your breath|"
    r"maybe a lag|trick of|quiet|still)\b",
    re.I,
)
JUMPSCARE_RE = re.compile(
    r"\b(lunged|scream|opened|mine|behind you|grab|face|don't look|smiled|lunged)\b",
    re.I,
)

DEFAULT_RESEMBLE_PROMPT = (
    "Tense faceless horror narrator for a YouTube Short. "
    "Whispered dread in the hook, slow uneasy pacing through the middle, "
    "brief false-calm drop, then sharp fear on scare lines — timing varies each video. "
    "Intimate close-mic feel — not cheerful, not news anchor, not monotone."
)

EDGE_HORROR_VOICE = "en-US-AndrewNeural"


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _is_scare_line(index: int, total: int, sentence: str, scare_indices: set[int] | None) -> bool:
    if scare_indices and index in scare_indices:
        return True
    if index == total - 1:
        return True
    return bool(JUMPSCARE_RE.search(sentence.lower()))


def edge_horror_prosody(
    sentence: str,
    *,
    index: int,
    total: int,
    scare_indices: set[int] | None = None,
) -> tuple[str, str]:
    """Per-sentence edge-tts rate/pitch (Communicate args, not SSML)."""
    lower = sentence.lower()
    if index == 0:
        return "-6%", "-3Hz"
    if _is_scare_line(index, total, sentence, scare_indices):
        return "+4%", "+0Hz"
    if FALSE_CALM_RE.search(lower):
        return "-14%", "-5Hz"
    return "-10%", "-4Hz"


def resemble_sentence_prosody(
    sentence: str,
    *,
    index: int,
    total: int,
    scare_indices: set[int] | None = None,
) -> tuple[str, str, str]:
    lower = sentence.lower()
    if index == 0:
        return "medium", "-1st", "medium"
    if _is_scare_line(index, total, sentence, scare_indices):
        return "fast", "+1st", "loud"
    if FALSE_CALM_RE.search(lower):
        return "slow", "-2st", "soft"
    return "slow", "-1st", "medium"


def _break_after(
    sentence: str,
    *,
    index: int,
    total: int,
    scare_indices: set[int] | None = None,
) -> str:
    lower = sentence.lower()
    if index == total - 1:
        return "120ms"
    if FALSE_CALM_RE.search(lower):
        return "400ms"
    if _is_scare_line(index, total, sentence, scare_indices):
        return "100ms"
    if index == 0:
        return "260ms"
    return "200ms"


def prepare_horror_resemble_ssml(
    plain_text: str,
    *,
    prompt: str | None = None,
    scare_indices: set[int] | None = None,
) -> str:
    sentences = _split_sentences(plain_text) or [plain_text.strip()]
    total = len(sentences)
    body_parts: list[str] = []
    for i, sentence in enumerate(sentences):
        rate, pitch, volume = resemble_sentence_prosody(
            sentence, index=i, total=total, scare_indices=scare_indices
        )
        safe = _escape_xml(sentence)
        is_scare = _is_scare_line(i, total, sentence, scare_indices)
        if is_scare:
            inner = (
                f'<prosody rate="{rate}" pitch="{pitch}" volume="{volume}">'
                f"<emphasis level='strong'>{safe}</emphasis></prosody>"
            )
        else:
            inner = f'<prosody rate="{rate}" pitch="{pitch}" volume="{volume}">{safe}</prosody>'
        body_parts.append(inner)
        if i < total - 1:
            body_parts.append(
                f'<break time="{_break_after(sentence, index=i, total=total, scare_indices=scare_indices)}"/>'
            )

    primer = prompt or DEFAULT_RESEMBLE_PROMPT
    return (
        f'<speak prompt="{_escape_xml(primer)}" exaggeration="0.72" temperature="0.75">\n'
        + "\n".join(body_parts)
        + "\n</speak>"
    )


def prepare_horror_plain_text(plain_text: str) -> str:
    """Light punctuation pacing for providers without SSML (edge plain mode)."""
    sentences = _split_sentences(plain_text) or [plain_text.strip()]
    out: list[str] = []
    for i, sentence in enumerate(sentences):
        if FALSE_CALM_RE.search(sentence) and i > 0:
            out.append("...")
        out.append(sentence)
    return " ".join(out)


def is_ssml(text: str) -> bool:
    return text.lstrip().startswith("<speak")
