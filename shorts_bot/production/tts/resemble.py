"""Resemble AI voice clone — paid TTS (your cloned voice)."""

from __future__ import annotations

import base64
import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

SYNTH_URL = "https://f.cluster.resemble.ai/synthesize"
VOICES_URL = "https://app.resemble.ai/api/v2/voices"
MAX_CHARS = 1900


def _post_json(url: str, payload: dict, *, api_key: str) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_json(url: str, *, api_key: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _chunk_text(text: str, max_len: int = MAX_CHARS) -> list[str]:
    if len(text) <= max_len:
        return [text]
    chunks: list[str] = []
    current = ""
    for sentence in text.replace("?", ".").replace("!", ".").split("."):
        part = sentence.strip()
        if not part:
            continue
        part = part + "."
        if len(current) + len(part) + 1 > max_len:
            if current:
                chunks.append(current.strip())
            current = part
        else:
            current = (current + " " + part).strip()
    if current:
        chunks.append(current.strip())
    return chunks or [text[:max_len]]


def _decode_audio(data: dict, tmp_dir: Path, index: int) -> Path:
    audio_b64 = data.get("audio_content")
    if not audio_b64:
        raise RuntimeError(f"Resemble returned no audio: {data}")
    fmt = (data.get("output_format") or "mp3").lower()
    raw = base64.b64decode(audio_b64)
    path = tmp_dir / f"_chunk_{index}.{fmt}"
    path.write_bytes(raw)
    return path


def _concat_mp3(parts: list[Path], out_path: Path) -> None:
    if len(parts) == 1 and parts[0].suffix.lower() == ".mp3":
        parts[0].rename(out_path)
        return
    list_file = out_path.parent / "_resemble_concat.txt"
    lines = [f"file '{p.resolve()}'" for p in parts]
    list_file.write_text("\n".join(["ffconcat version 1.0", *lines]) + "\n", encoding="utf-8")
    cmd = [
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
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    list_file.unlink(missing_ok=True)
    for p in parts:
        p.unlink(missing_ok=True)


def synthesize_resemble(text: str, out_path: Path) -> tuple[str, str]:
    from shorts_bot.config import settings

    api_key = (settings.resemble_api_key or "").strip()
    voice_uuid = (settings.resemble_voice_uuid or "").strip()
    if not api_key or not voice_uuid:
        raise ValueError("RESEMBLE_API_KEY and RESEMBLE_VOICE_UUID required for voice clone.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = out_path.parent / "_resemble_tmp"
    tmp_dir.mkdir(exist_ok=True)

    chunk_paths: list[Path] = []
    try:
        for i, chunk in enumerate(_chunk_text(text)):
            payload = {
                "voice_uuid": voice_uuid,
                "data": chunk,
                "output_format": "mp3",
                "sample_rate": settings.resemble_sample_rate,
                "use_hd": settings.resemble_use_hd,
            }
            if settings.resemble_project_uuid:
                payload["project_uuid"] = settings.resemble_project_uuid
            try:
                data = _post_json(SYNTH_URL, payload, api_key=api_key)
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"Resemble API error {exc.code}: {body[:300]}") from exc
            chunk_paths.append(_decode_audio(data, tmp_dir, i))

        _concat_mp3(chunk_paths, out_path)
    finally:
        if tmp_dir.exists():
            for leftover in tmp_dir.glob("*"):
                leftover.unlink(missing_ok=True)
            tmp_dir.rmdir()

    return (
        "resemble-clone",
        f"Resemble voice clone saved {out_path.name} (voice {voice_uuid[:8]}…)",
    )


def list_voices(api_key: str) -> list[dict]:
    """List voices on Resemble account (for setup CLI)."""
    try:
        data = _get_json(VOICES_URL, api_key=api_key)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Resemble voices API {exc.code}: {body[:300]}") from exc
    items = data.get("items") or data.get("voices") or []
    return items if isinstance(items, list) else []


def probe_resemble(api_key: str, voice_uuid: str) -> tuple[bool, str]:
    """Quick synthesis test (one short phrase)."""
    try:
        data = _post_json(
            SYNTH_URL,
            {
                "voice_uuid": voice_uuid,
                "data": "Soft Continuity voice check.",
                "output_format": "mp3",
                "sample_rate": 44100,
            },
            api_key=api_key,
        )
        if data.get("audio_content"):
            return True, "Resemble voice clone responds"
        return False, f"Unexpected response: {str(data)[:120]}"
    except Exception as exc:
        return False, str(exc)[:200]
