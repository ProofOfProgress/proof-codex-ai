import base64
import io
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import urllib.error

from shorts_bot.production.tts.resemble import _chunk_text, synthesize_resemble


def test_chunk_text_splits_long_script():
    long = ("Word. " * 500).strip()
    chunks = _chunk_text(long, max_len=100)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)


def test_synthesize_resemble_writes_mp3(tmp_path: Path, monkeypatch):
    fake_audio = b"fake-mp3-bytes"
    payload = {"audio_content": base64.b64encode(fake_audio).decode(), "output_format": "mp3"}

    def fake_post(url, body, *, api_key):
        return payload

    monkeypatch.setattr(
        "shorts_bot.production.tts.resemble._post_json",
        fake_post,
    )

    class FakeSettings:
        resemble_api_key = "test-key-abcdefghij"
        resemble_voice_uuid = "voice-uuid-12345678"
        resemble_project_uuid = None
        resemble_sample_rate = 44100
        resemble_use_hd = False

    monkeypatch.setattr("shorts_bot.config.settings", FakeSettings())

    out = tmp_path / "voiceover.mp3"
    with patch("subprocess.run") as run:
        run.return_value = MagicMock(returncode=0)
        # Single mp3 chunk renames without ffmpeg
        provider, msg = synthesize_resemble("Hello from my clone.", out)
    assert provider == "resemble-clone"
    assert out.exists()
    assert out.read_bytes() == fake_audio


def test_post_json_retries_on_429(monkeypatch):
    from shorts_bot.production.tts.resemble import _post_json

    calls = {"n": 0}

    def fake_urlopen(req, timeout=120):
        calls["n"] += 1
        if calls["n"] == 1:
            raise urllib.error.HTTPError(req.full_url, 429, "rate limit", hdrs=None, fp=io.BytesIO(b"busy"))
        return io.BytesIO(json.dumps({"ok": True}).encode())

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr("shorts_bot.production.tts.resemble.time.sleep", lambda _s: None)

    data = _post_json("https://example.test/synth", {"data": "hi"}, api_key="test-key")
    assert data["ok"] is True
    assert calls["n"] == 2
