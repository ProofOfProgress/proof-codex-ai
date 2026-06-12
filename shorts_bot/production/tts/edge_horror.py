"""Edge-tts horror delivery — per-sentence prosody (SSML is too slow in edge-tts)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from shorts_bot.production.tts.edge import synthesize_edge
from shorts_bot.production.tts.horror_voice import EDGE_HORROR_VOICE, _split_sentences, edge_horror_prosody


def _concat_mp3(parts: list[Path], out_path: Path) -> None:
    if len(parts) == 1:
        parts[0].replace(out_path)
        return
    list_file = out_path.parent / "_edge_horror_concat.txt"
    lines = [f"file '{p.resolve()}'" for p in parts]
    list_file.write_text("\n".join(["ffconcat version 1.0", *lines]) + "\n", encoding="utf-8")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(out_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    list_file.unlink(missing_ok=True)
    for p in parts:
        p.unlink(missing_ok=True)


def synthesize_horror_edge(
    plain_text: str,
    out_path: Path,
    *,
    voice: str | None = None,
    scare_indices: set[int] | None = None,
) -> tuple[str, str]:
    """One edge call per sentence with dread/lunge prosody; concat to one MP3."""
    voice = voice or EDGE_HORROR_VOICE
    sentences = _split_sentences(plain_text) or [plain_text.strip()]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.parent / "_edge_horror_tmp"
    tmp.mkdir(exist_ok=True)
    parts: list[Path] = []
    total = len(sentences)
    try:
        for i, sentence in enumerate(sentences):
            rate, pitch = edge_horror_prosody(
                sentence, index=i, total=total, scare_indices=scare_indices
            )
            part = tmp / f"line_{i:02d}.mp3"
            synthesize_edge(sentence, part, voice=voice, rate=rate, pitch=pitch)
            parts.append(part)
        _concat_mp3(parts, out_path)
    finally:
        if tmp.exists():
            for leftover in tmp.glob("*"):
                leftover.unlink(missing_ok=True)
            tmp.rmdir()

    return (
        "edge-tts",
        f"edge-tts horror pacing saved {out_path.name} ({voice}, {len(sentences)} beats)",
    )
