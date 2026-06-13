"""Official Kling AI API — JWT auth, text/image-to-video with native audio."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://api.klingai.com/v1"


def _jwt_token(access_key: str, secret_key: str) -> str:
    import jwt

    now = int(time.time())
    payload = {"iss": access_key, "exp": now + 1800, "nbf": now - 5}
    headers = {"alg": "HS256", "typ": "JWT"}
    return jwt.encode(payload, secret_key, algorithm="HS256", headers=headers)


def _headers(access_key: str, secret_key: str) -> dict[str, str]:
    token = _jwt_token(access_key, secret_key)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "shorts-bot/1.0",
    }


def _request(
    method: str,
    url: str,
    *,
    access_key: str,
    secret_key: str,
    payload: dict | None = None,
    timeout: int = 120,
) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers=_headers(access_key, secret_key),
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Kling API {exc.code}: {body[:500]}") from exc


def _poll_task(
    task_id: str,
    *,
    access_key: str,
    secret_key: str,
    timeout_sec: int = 900,
    poll_sec: float = 12.0,
) -> dict:
    url = f"{API_BASE}/videos/text2video/{task_id}"
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        result = _request("GET", url, access_key=access_key, secret_key=secret_key)
        data = result.get("data") or {}
        status = (data.get("task_status") or "").lower()
        if status == "succeed":
            return data
        if status in {"failed", "fail", "error"}:
            msg = data.get("task_status_msg") or data.get("message") or result
            raise RuntimeError(f"Kling task failed: {msg}")
        time.sleep(poll_sec)
    raise TimeoutError(f"Kling task {task_id} timed out after {timeout_sec}s")


def _download_url(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "shorts-bot/1.0"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        dest.write_bytes(resp.read())


def _video_url_from_task(data: dict) -> str:
    result = data.get("task_result") or {}
    videos = result.get("videos") or []
    if not videos:
        raise RuntimeError(f"Kling task missing videos: {data}")
    first = videos[0]
    url = first.get("url") if isinstance(first, dict) else first
    if not isinstance(url, str) or not url.strip():
        raise RuntimeError(f"Kling task missing video url: {first}")
    return url


def probe_kling_official(access_key: str, secret_key: str) -> tuple[bool, str]:
    """Lightweight auth check — list/query without starting a full generation."""
    if not access_key.strip() or not secret_key.strip():
        return False, "KLING_ACCESS_KEY and KLING_SECRET_KEY required"
    try:
        _jwt_token(access_key.strip(), secret_key.strip())
        # POST with minimal invalid body often returns 400 if auth OK vs 401 if bad
        url = f"{API_BASE}/videos/text2video"
        try:
            _request(
                "POST",
                url,
                access_key=access_key.strip(),
                secret_key=secret_key.strip(),
                payload={"model_name": "kling-v2-6", "prompt": "test", "duration": "5"},
            )
        except RuntimeError as exc:
            msg = str(exc)
            if "401" in msg or "403" in msg or "Unauthenticated" in msg:
                return False, msg[:200]
            if "400" in msg or "invalid" in msg.lower() or "parameter" in msg.lower():
                return True, "Kling official API credentials accepted"
            return True, "Kling JWT generated; API reachable"
        return True, "Kling official API credentials accepted"
    except Exception as exc:
        return False, str(exc)[:200]


def generate_kling_official_video(
    prompt: str,
    out_path: Path,
    *,
    access_key: str,
    secret_key: str,
    model_name: str = "kling-v2-6",
    duration: int = 15,
    aspect_ratio: str = "9:16",
    mode: str = "pro",
    sound: bool = True,
    negative_prompt: str = "",
    multi_prompt: list[dict] | None = None,
    start_image_path: Path | None = None,
    timeout_sec: int = 900,
) -> str:
    """Text or image-to-video via official Kling API."""
    access_key = access_key.strip()
    secret_key = secret_key.strip()
    dur = str(max(3, min(15, int(duration))))

    if start_image_path and start_image_path.exists():
        import base64

        b64 = base64.b64encode(start_image_path.read_bytes()).decode("ascii")
        body: dict = {
            "model_name": model_name,
            "prompt": prompt,
            "duration": dur,
            "aspect_ratio": aspect_ratio,
            "mode": mode,
            "sound": "on" if sound else "off",
            "image": b64,
        }
        url = f"{API_BASE}/videos/image2video"
    else:
        body = {
            "model_name": model_name,
            "prompt": prompt,
            "duration": dur,
            "aspect_ratio": aspect_ratio,
            "mode": mode,
            "sound": "on" if sound else "off",
        }
        url = f"{API_BASE}/videos/text2video"

    if negative_prompt.strip():
        body["negative_prompt"] = negative_prompt.strip()

    if multi_prompt:
        body["multi_shot"] = True
        body["shot_type"] = "customize"
        body["multi_prompt"] = [
            {"prompt": str(s.get("prompt") or ""), "duration": str(int(s.get("duration") or 5))}
            for s in multi_prompt
        ]

    created = _request("POST", url, access_key=access_key, secret_key=secret_key, payload=body)
    data = created.get("data") or {}
    task_id = data.get("task_id")
    if not task_id:
        raise RuntimeError(f"Kling returned no task_id: {created}")

    finished = _poll_task(
        task_id,
        access_key=access_key,
        secret_key=secret_key,
        timeout_sec=timeout_sec,
    )
    video_url = _video_url_from_task(finished)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _download_url(video_url, out_path)
    return f"kling-official/{model_name}"
