from pathlib import Path
import time

from shorts_bot.production.transcript_sync import _read_cache, _write_cache


def test_transcript_cache_invalid_when_voiceover_newer(tmp_path: Path):
    audio = tmp_path / "voiceover.mp3"
    audio.write_bytes(b"audio-v2")
    _write_cache(audio, "0:01 old transcript line")
    time.sleep(0.05)
    audio.write_bytes(b"audio-v3-regenerated")
    audio.touch()
    assert _read_cache(audio) is None


def test_transcript_cache_hits_when_fresh(tmp_path: Path):
    audio = tmp_path / "voiceover.mp3"
    audio.write_bytes(b"audio")
    _write_cache(audio, "0:01 fresh line")
    hit = _read_cache(audio)
    assert hit is not None
    assert "fresh line" in hit.transcript_text
