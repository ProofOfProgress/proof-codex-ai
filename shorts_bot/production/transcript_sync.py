"""Word-level transcript sync — AssemblyAI API only (no browser)."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.turboscribe_parser import format_timestamp_lines


@dataclass
class TranscriptResult:
    transcript_text: str
    source: str
    message: str


def _cached_transcript_paths(audio_path: Path) -> list[Path]:
    parent = audio_path.parent
    return [parent / "transcript.txt", parent / "turboscribe_transcript.txt"]


def _cached_transcript_path(audio_path: Path) -> Path:
    return audio_path.parent / "transcript.txt"


def _read_cache(audio_path: Path) -> TranscriptResult | None:
    for path in _cached_transcript_paths(audio_path):
        if path.exists():
            text = path.read_text(encoding="utf-8").strip()
            if text:
                return TranscriptResult(
                    transcript_text=text,
                    source="cache",
                    message=f"Using cached {path.name}",
                )
    return None


def _words_to_timestamp_lines(words: list[dict]) -> str:
    """Group AssemblyAI words into M:SS lines for parse_turboscribe."""
    if not words:
        return ""
    lines: list[tuple[float, str]] = []
    bucket_start = float(words[0].get("start", 0) or 0) / 1000.0
    bucket_words: list[str] = []
    max_span = 2.5

    for w in words:
        text = (w.get("text") or "").strip()
        if not text:
            continue
        start_ms = float(w.get("start", 0) or 0)
        start_sec = start_ms / 1000.0
        if bucket_words and start_sec - bucket_start >= max_span:
            lines.append((bucket_start, " ".join(bucket_words)))
            bucket_start = start_sec
            bucket_words = []
        bucket_words.append(text)

    if bucket_words:
        lines.append((bucket_start, " ".join(bucket_words)))

    return format_timestamp_lines(lines)


def _assemblyai_json(
    method: str,
    url: str,
    *,
    api_key: str,
    body: dict | None = None,
    raw: bytes | None = None,
    content_type: str = "application/json",
) -> dict:
    headers = {"authorization": api_key}
    data: bytes | None = None
    if raw is not None:
        headers["content-type"] = content_type
        data = raw
    elif body is not None:
        headers["content-type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"AssemblyAI HTTP {exc.code}: {detail}") from exc


def transcribe_with_assemblyai(audio_path: Path, *, timeout_sec: int = 600) -> TranscriptResult:
    """Upload MP3 to AssemblyAI and return timestamped transcript text."""
    key = (settings.assemblyai_api_key or "").strip()
    if not key:
        raise RuntimeError("ASSEMBLYAI_API_KEY missing — add to .env and sync_secrets")

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio not found: {audio_path}")

    model = (settings.assemblyai_speech_model or "universal").strip()
    audio_path = audio_path.resolve()
    up = _assemblyai_json(
        "POST",
        "https://api.assemblyai.com/v2/upload",
        api_key=key,
        raw=audio_path.read_bytes(),
        content_type="application/octet-stream",
    )
    upload_url = up.get("upload_url")
    if not upload_url:
        raise RuntimeError("AssemblyAI upload failed — no upload_url")

    job = _assemblyai_json(
        "POST",
        "https://api.assemblyai.com/v2/transcript",
        api_key=key,
        body={"audio_url": upload_url, "speech_model": model},
    )
    transcript_id = job.get("id")
    if not transcript_id:
        raise RuntimeError("AssemblyAI transcript job missing id")

    deadline = time.time() + timeout_sec
    status = "queued"
    while time.time() < deadline:
        payload = _assemblyai_json(
            "GET",
            f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
            api_key=key,
        )
        status = payload.get("status") or ""
        if status == "completed":
            words = payload.get("words") or []
            if words:
                text = _words_to_timestamp_lines(words)
            else:
                text = (payload.get("text") or "").strip()
            if not text.strip():
                raise RuntimeError("AssemblyAI returned empty transcript")
            out_path = _cached_transcript_path(audio_path)
            out_path.write_text(text.strip() + "\n", encoding="utf-8")
            legacy = audio_path.parent / "turboscribe_transcript.txt"
            if legacy != out_path:
                legacy.write_text(text.strip() + "\n", encoding="utf-8")
            return TranscriptResult(
                transcript_text=text.strip(),
                source="assemblyai",
                message=f"AssemblyAI ({model}) sync saved → {out_path.name}",
            )
        if status == "error":
            raise RuntimeError(f"AssemblyAI failed: {payload.get('error') or 'unknown'}")
        time.sleep(3)

    raise RuntimeError(f"AssemblyAI transcript timed out after {timeout_sec}s (last status: {status})")


def transcribe_audio(audio_path: Path) -> TranscriptResult:
    """Transcribe voiceover via AssemblyAI API."""
    if not settings.transcript_always_fresh:
        cached = _read_cache(audio_path)
        if cached:
            return cached
    return transcribe_with_assemblyai(audio_path)
