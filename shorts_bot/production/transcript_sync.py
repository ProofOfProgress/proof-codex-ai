"""Timestamped transcript sync — Gemini audio (default) or optional AssemblyAI API."""

from __future__ import annotations

import base64
import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.turboscribe_parser import format_timestamp_lines, parse_turboscribe


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


def _write_cache(audio_path: Path, text: str) -> Path:
    out_path = _cached_transcript_path(audio_path)
    out_path.write_text(text.strip() + "\n", encoding="utf-8")
    legacy = audio_path.parent / "turboscribe_transcript.txt"
    if legacy != out_path:
        legacy.write_text(text.strip() + "\n", encoding="utf-8")
    return out_path


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


def _normalize_gemini_transcript(raw: str) -> str:
    """Convert Gemini timestamp output to M:SS lines for parse_turboscribe."""
    lines_out: list[tuple[float, str]] = []
    for line in raw.splitlines():
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        text = re.sub(r"^[-*•]\s*", "", text)
        m = re.match(
            r"^\[?(?:(\d+):)?(\d{1,2}):(\d{2})(?:[.,](\d+))?\]?\s*[-–:]?\s*(.+)$",
            text,
        )
        if m:
            h = int(m.group(1) or 0)
            mins = int(m.group(2))
            secs = int(m.group(3))
            frac = int((m.group(4) or "0")[:1])
            start = h * 3600 + mins * 60 + secs + frac / 10.0
            spoken = m.group(5).strip()
            if spoken:
                lines_out.append((start, spoken))
            continue
        m2 = re.match(r"^(\d{1,2}):(\d{2})\s+(.+)$", text)
        if m2:
            start = int(m2.group(1)) * 60 + int(m2.group(2))
            lines_out.append((start, m2.group(3).strip()))
    if lines_out:
        return format_timestamp_lines(lines_out)
    return raw.strip()


def _validate_transcript(text: str) -> str:
    cleaned = _normalize_gemini_transcript(text)
    if parse_turboscribe(cleaned):
        return cleaned.strip()
    if parse_turboscribe(text):
        return text.strip()
    raise RuntimeError("Transcript missing parseable timestamps (M:SS lines)")


def _gemini_generate_content(model: str, body: dict) -> dict:
    key = (settings.gemini_api_key or "").strip()
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        f"?key={key}"
    )
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
        raise RuntimeError(f"Gemini transcript HTTP {exc.code}: {detail}") from exc


def transcribe_with_gemini(audio_path: Path) -> TranscriptResult:
    """Transcribe voiceover via Gemini audio understanding (same key as chat/vision)."""
    if not settings.has_gemini:
        raise RuntimeError("GEMINI_API_KEY missing — add to Cursor secrets; install.sh syncs it")

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio not found: {audio_path}")

    audio_bytes = audio_path.read_bytes()
    if len(audio_bytes) > 18 * 1024 * 1024:
        raise RuntimeError("Voiceover too large for inline Gemini audio")

    model = (settings.gemini_transcript_model or settings.gemini_model).strip()
    mime = "audio/mpeg" if audio_path.suffix.lower() in {".mp3", ".mpeg"} else "audio/mp4"
    prompt = (
        "Transcribe this voiceover. Output ONLY lines in format: M:SS words spoken\n"
        "Example:\n0:00 the minute before\n0:03 you breathe once\n"
        "Chunk phrases every 2-4 seconds at natural pauses. No commentary."
    )
    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mime, "data": base64.standard_b64encode(audio_bytes).decode()}},
                ]
            }
        ],
        # audioTimestamp is Vertex-only — not supported on Gemini Developer API (API key).
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1200,
        },
    }
    payload = _gemini_generate_content(model, body)
    candidates = payload.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"Gemini transcript empty response: {payload.get('error', payload)[:200]}")
    parts = (candidates[0].get("content") or {}).get("parts") or []
    raw = "".join(str(p.get("text", "")) for p in parts).strip()
    if not raw:
        raise RuntimeError("Gemini returned empty transcript")

    text = _validate_transcript(raw)
    out_path = _write_cache(audio_path, text)
    return TranscriptResult(
        transcript_text=text,
        source="gemini",
        message=f"Gemini ({model}) transcript saved → {out_path.name}",
    )


def _words_to_timestamp_lines(words: list[dict]) -> str:
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
    """Optional fallback when ASSEMBLYAI_API_KEY is in Cursor secrets."""
    key = (settings.assemblyai_api_key or "").strip()
    if not key:
        raise RuntimeError("ASSEMBLYAI_API_KEY not set")

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
            text = _validate_transcript(text)
            out_path = _write_cache(audio_path, text)
            return TranscriptResult(
                transcript_text=text,
                source="assemblyai",
                message=f"AssemblyAI ({model}) sync saved → {out_path.name}",
            )
        if status == "error":
            raise RuntimeError(f"AssemblyAI failed: {payload.get('error') or 'unknown'}")
        time.sleep(3)

    raise RuntimeError(f"AssemblyAI transcript timed out after {timeout_sec}s (last status: {status})")


def transcribe_audio(audio_path: Path) -> TranscriptResult:
    """Transcribe voiceover — Gemini by default (no extra signup)."""
    if not settings.transcript_always_fresh:
        cached = _read_cache(audio_path)
        if cached:
            return cached

    provider = (settings.transcript_provider or "gemini").strip().lower()
    if provider == "assemblyai" and settings.has_assemblyai:
        return transcribe_with_assemblyai(audio_path)
    if settings.has_gemini:
        return transcribe_with_gemini(audio_path)
    if settings.has_assemblyai:
        return transcribe_with_assemblyai(audio_path)
    raise RuntimeError(
        "Transcript sync needs GEMINI_API_KEY in Cursor secrets (same key as chat/vision). "
        "Run: bash scripts/install.sh"
    )
