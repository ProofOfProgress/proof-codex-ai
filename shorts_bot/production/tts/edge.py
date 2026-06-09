"""Free Microsoft Edge neural TTS."""

from __future__ import annotations

import asyncio
from pathlib import Path


async def _run(text: str, out_path: Path, *, voice: str, rate: str, pitch: str) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(str(out_path))


def synthesize_edge(
    text: str,
    out_path: Path,
    *,
    voice: str,
    rate: str = "-5%",
    pitch: str = "+0Hz",
) -> tuple[str, str]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(_run(text, out_path, voice=voice, rate=rate, pitch=pitch))
    return ("edge-tts", f"edge-tts saved {out_path.name} ({voice})")
