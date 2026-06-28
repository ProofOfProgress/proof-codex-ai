"""Kling official API — image-to-video for TikTok Shop clips."""

from __future__ import annotations

import json
import subprocess
import time
from typing import Any

import httpx

from shorts_bot.config import settings

API_BASE = "https://api.klingai.com/v1"
OFFICIAL_I2V_DEFAULT = "kling-v2-6"
REQUIRED_ASPECT_RATIO = "9:16"
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
ASPECT_TOLERANCE = 0.03

# Official image2video model_name values (Kling OpenAPI). Course default: v2.6.
OFFICIAL_I2V_MODELS: frozenset[str] = frozenset(
    {
        "kling-v1",
        "kling-v1-5",
        "kling-v1-6",
        "kling-v2-master",
        "kling-v2-1",
        "kling-v2-1-master",
        "kling-v2-5-turbo",
        "kling-v2-6",
        "kling-v3",
    }
)


def resolve_model_name(model_name: str | None = None) -> str:
    """
    Map settings to a valid official API model_name.
    Replicate slugs (e.g. kwaivgi/kling-v3-video) are not valid on api.klingai.com.
    """
    raw = (model_name or settings.kling_model or OFFICIAL_I2V_DEFAULT).strip()
    provider = (settings.kling_provider or "official").strip().lower()
    if provider != "official":
        return raw
    if "/" in raw or raw.startswith("kwaivgi"):
        return OFFICIAL_I2V_DEFAULT
    if raw in OFFICIAL_I2V_MODELS:
        return raw
    if raw.startswith("kling-"):
        return raw
    return OFFICIAL_I2V_DEFAULT


def normalize_aspect_ratio(aspect_ratio: str | None) -> str:
    """Affiliate clips are always 9:16 — reject any other ratio."""
    raw = (aspect_ratio or settings.kling_aspect_ratio or REQUIRED_ASPECT_RATIO).strip()
    normalized = raw.replace(" ", "").lower()
    allowed = {"9:16", "9/16", "916", "vertical", "portrait"}
    if normalized not in allowed:
        raise ValueError(
            f"Kling aspect ratio must be 9:16 for TikTok Shop — got {raw!r}. "
            "Set KLING_ASPECT_RATIO=9:16 in Secrets."
        )
    return REQUIRED_ASPECT_RATIO


def probe_video_size(path) -> tuple[int, int]:
    """Return (width, height) via ffprobe."""
    from pathlib import Path

    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(p)
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "json",
            str(p),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {proc.stderr[:300]}")
    data = json.loads(proc.stdout or "{}")
    streams = data.get("streams") or []
    if not streams:
        raise RuntimeError(f"No video stream in {p}")
    w = int(streams[0].get("width") or 0)
    h = int(streams[0].get("height") or 0)
    if w <= 0 or h <= 0:
        raise RuntimeError(f"Invalid video dimensions for {p}: {w}x{h}")
    return w, h


def assert_vertical_916(path, *, label: str = "Kling output") -> tuple[int, int]:
    """Raise if downloaded clip is not vertical 9:16."""
    w, h = probe_video_size(path)
    ratio = w / h
    target = 9 / 16
    if abs(ratio - target) > ASPECT_TOLERANCE:
        raise RuntimeError(
            f"{label} must be 9:16 vertical — got {w}x{h} (ratio {ratio:.3f}). "
            "Check KLING_ASPECT_RATIO=9:16 and Module 4 image is full-bleed 9:16."
        )
    if w < 540 or h < 960:
        raise RuntimeError(f"{label} resolution too low — got {w}x{h}")
    return w, h


def configured() -> bool:
    return settings.has_kling_official


def _auth_header() -> dict[str, str]:
    if not configured():
        raise RuntimeError("Kling not configured — set KLING_API_KEY or ACCESS+SECRET in Secrets")
    ak = (settings.kling_access_key or "").strip()
    sk = (settings.kling_secret_key or "").strip()
    if ak and sk and "your-" not in (ak + sk).lower():
        # Official API credits usually sit on Access Key + Secret (JWT), not the single API key.
        import jwt

        payload = {"iss": ak, "exp": int(time.time()) + 1800, "nbf": int(time.time()) - 5}
        token = jwt.encode(payload, sk, algorithm="HS256")
        return {"Authorization": f"Bearer {token}"}
    bearer = (settings.kling_api_key or "").strip()
    if bearer:
        return {"Authorization": f"Bearer {bearer}"}
    raise RuntimeError("Kling not configured — set KLING_ACCESS_KEY + KLING_SECRET_KEY or KLING_API_KEY")


def _headers() -> dict[str, str]:
    return {**_auth_header(), "Content-Type": "application/json"}


def create_image2video(
    *,
    image_url: str,
    prompt: str,
    negative_prompt: str = "",
    duration: int | None = None,
    aspect_ratio: str | None = None,
    mode: str | None = None,
    model_name: str | None = None,
    sound: str | None = None,
) -> str:
    """Submit image2video job; return task_id."""
    dur = str(duration or settings.kling_clip_seconds or 5)
    if dur not in {"5", "10"}:
        dur = "5" if int(dur) <= 5 else "10"
    ratio = normalize_aspect_ratio(aspect_ratio)
    body = {
        "model_name": resolve_model_name(model_name),
        "image": image_url.strip(),
        "prompt": prompt.strip(),
        "duration": dur,
        "aspect_ratio": ratio,
        "mode": mode or settings.kling_mode or "std",
    }
    neg = (negative_prompt or "").strip()
    if neg:
        body["negative_prompt"] = neg
    if sound is not None:
        body["sound"] = sound
    elif not settings.kling_generate_audio:
        body["sound"] = "off"

    with httpx.Client(timeout=60.0) as client:
        resp = client.post(f"{API_BASE}/videos/image2video", headers=_headers(), json=body)
    data = _parse_body(resp)
    task_id = _task_id(data)
    if not task_id:
        raise RuntimeError(f"Kling create task missing task_id: {data}")
    return task_id


def get_image2video_task(task_id: str) -> dict[str, Any]:
    with httpx.Client(timeout=60.0) as client:
        resp = client.get(
            f"{API_BASE}/videos/image2video/{task_id.strip()}",
            headers=_auth_header(),
        )
    return _parse_body(resp)


def wait_for_video_url(
    task_id: str,
    *,
    poll_sec: float = 8.0,
    timeout_sec: int = 600,
) -> str:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        body = get_image2video_task(task_id)
        status = _task_status(body)
        if status in {"succeed", "success", "completed"}:
            url = _video_url(body)
            if url:
                return url
            raise RuntimeError(f"Kling task succeeded but no video URL: {body}")
        if status in {"failed", "fail", "error"}:
            raise RuntimeError(f"Kling task failed: {body.get('message') or body}")
        time.sleep(poll_sec)
    raise TimeoutError(f"Kling task {task_id} timed out after {timeout_sec}s")


def download_video(url: str, dest) -> None:
    from pathlib import Path

    path = Path(dest)
    path.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=120.0, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        path.write_bytes(resp.content)
    assert_vertical_916(path, label="Kling download")


def _parse_body(resp: httpx.Response) -> dict[str, Any]:
    try:
        body = resp.json()
    except Exception as exc:
        raise RuntimeError(f"Kling non-JSON ({resp.status_code}): {resp.text[:200]}") from exc
    if resp.status_code >= 400 or body.get("code") not in (0, None):
        msg = body.get("message") or body
        raise RuntimeError(f"Kling error: {msg}")
    return body if isinstance(body, dict) else {}


def _task_id(body: dict[str, Any]) -> str:
    data = body.get("data")
    if isinstance(data, dict):
        for key in ("task_id", "taskId", "id"):
            val = data.get(key)
            if val:
                return str(val)
    for key in ("task_id", "taskId"):
        if body.get(key):
            return str(body[key])
    return ""


def _task_status(body: dict[str, Any]) -> str:
    data = body.get("data")
    if isinstance(data, dict):
        for key in ("task_status", "status", "state"):
            if data.get(key):
                return str(data[key]).lower()
    return str(body.get("task_status") or body.get("status") or "").lower()


def _video_url(body: dict[str, Any]) -> str:
    data = body.get("data")
    if not isinstance(data, dict):
        return ""
    result = data.get("task_result") or data.get("result") or {}
    if isinstance(result, dict):
        videos = result.get("videos") or result.get("video_list") or []
        if isinstance(videos, list) and videos:
            first = videos[0]
            if isinstance(first, dict):
                for key in ("url", "video_url", "watermark_url"):
                    if first.get(key):
                        return str(first[key])
        for key in ("video_url", "url"):
            if result.get(key):
                return str(result[key])
    for key in ("video_url", "url"):
        if data.get(key):
            return str(data[key])
    return ""
