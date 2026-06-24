"""Kling official API — image-to-video for TikTok Shop clips."""

from __future__ import annotations

import time
from typing import Any

import httpx

from shorts_bot.config import settings

API_BASE = "https://api.klingai.com/v1"


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
    body = {
        "model_name": model_name or "kling-v2-6",
        "image": image_url.strip(),
        "prompt": prompt.strip(),
        "duration": dur,
        "aspect_ratio": aspect_ratio or settings.kling_aspect_ratio or "9:16",
        "mode": mode or settings.kling_mode or "std",
    }
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
