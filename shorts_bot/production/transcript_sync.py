"""Word-level transcript sync — AssemblyAI API (default) or TurboScribe browser fallback."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.turboscribe_sync import (
    TurboScribeResult,
    _format_segments_for_parser,
    transcribe_audio as turboscribe_transcribe,
)


@dataclass
class TranscriptResult:
    transcript_text: str
    source: str
    message: str


def _cached_transcript_path(audio_path: Path) -> Path:
    return audio_path.parent / "turboscribe_transcript.txt"


def _read_cache(audio_path: Path) -> TranscriptResult | None:
    path = _cached_transcript_path(audio_path)
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None
    return TranscriptResult(
        transcript_text=text,
        source="cache",
        message=f"Using cached {path.name}",
    )


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

    return _format_segments_for_parser(lines)


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
        raise RuntimeError(
            "ASSEMBLYAI_API_KEY missing — set in .env or use TRANSCRIPT_PROVIDER=turboscribe"
        )

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio not found: {audio_path}")

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
        body={"audio_url": upload_url, "speech_model": "best"},
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
            return TranscriptResult(
                transcript_text=text.strip(),
                source="assemblyai",
                message=f"AssemblyAI sync saved → {out_path.name}",
            )
        if status == "error":
            raise RuntimeError(f"AssemblyAI failed: {payload.get('error') or 'unknown'}")
        time.sleep(3)

    raise RuntimeError(f"AssemblyAI transcript timed out after {timeout_sec}s (last status: {status})")


def transcribe_audio(audio_path: Path) -> TranscriptResult:
    """
    Transcribe voiceover with configured provider.

    Default: AssemblyAI API (no browser). Fallback: TurboScribe Playwright when
    TRANSCRIPT_PROVIDER=turboscribe.
    """
    always_fresh = settings.transcript_always_fresh or settings.turboscribe_always_fresh
    if not always_fresh:
        cached = _read_cache(audio_path)
        if cached:
            return cached

    provider = (settings.transcript_provider or "assemblyai").strip().lower()
    if provider == "turboscribe" or (
        provider != "assemblyai" and settings.use_turboscribe_sync and not settings.has_assemblyai
    ):
        ts: TurboScribeResult = turboscribe_transcribe(audio_path)
        return TranscriptResult(
            transcript_text=ts.transcript_text,
            source=ts.source,
            message=ts.message,
        )

    if provider == "assemblyai" or settings.has_assemblyai:
        return transcribe_with_assemblyai(audio_path)

    if settings.use_turboscribe_sync:
        ts = turboscribe_transcribe(audio_path)
        return TranscriptResult(
            transcript_text=ts.transcript_text,
            source=ts.source,
            message=ts.message,
        )

    raise RuntimeError(
        "No transcript provider configured. Set ASSEMBLYAI_API_KEY + TRANSCRIPT_PROVIDER=assemblyai "
        "or enable TurboScribe (TRANSCRIPT_PROVIDER=turboscribe + login_handoff)."
    )
