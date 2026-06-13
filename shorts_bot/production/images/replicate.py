"""Replicate FLUX images + MiniMax/Hailuo I2V clips (pay-per-run)."""

from __future__ import annotations

import json
import mimetypes
import time
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://api.replicate.com/v1"


def _parse_retry_after(body: str, code: int) -> float:
    try:
        data = json.loads(body)
        if isinstance(data.get("retry_after"), (int, float)):
            return max(1.0, float(data["retry_after"]))
    except json.JSONDecodeError:
        pass
    return 12.0 if code == 429 else 5.0


def _request(
    method: str,
    url: str,
    *,
    token: str,
    payload: dict | None = None,
    max_retries: int = 8,
) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "shorts-bot/1.0",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    last_error: Exception | None = None
    for attempt in range(max_retries):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code in {429, 502, 503, 504} and attempt < max_retries - 1:
                time.sleep(_parse_retry_after(body, exc.code))
                last_error = RuntimeError(f"Replicate API {exc.code}: {body[:400]}")
                continue
            raise RuntimeError(f"Replicate API {exc.code}: {body[:400]}") from exc
    if last_error:
        raise last_error
    raise RuntimeError("Replicate request failed after retries")


def _poll_prediction(prediction_id: str, *, token: str, timeout_sec: int = 300) -> dict:
    url = f"{API_BASE}/predictions/{prediction_id}"
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        data = _request("GET", url, token=token)
        status = data.get("status")
        if status == "succeeded":
            return data
        if status in {"failed", "canceled"}:
            raise RuntimeError(f"Replicate prediction {status}: {data.get('error')}")
        time.sleep(2)
    raise TimeoutError(f"Replicate prediction {prediction_id} timed out")


def _download_url(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "shorts-bot/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def _multipart_file_body(path: Path) -> tuple[bytes, str]:
    """Build multipart/form-data body for Replicate POST /v1/files."""
    boundary = "shortsbot" + str(int(time.time() * 1000))
    filename = path.name
    mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    file_bytes = path.read_bytes()
    parts: list[bytes] = [
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="content"; filename="{filename}"\r\n'
            f"Content-Type: {mime}\r\n\r\n"
        ).encode("utf-8"),
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8"),
    ]
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def upload_replicate_file(path: Path, *, token: str) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    body, content_type = _multipart_file_body(path)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": content_type,
        "User-Agent": "shorts-bot/1.0",
    }
    req = urllib.request.Request(
        f"{API_BASE}/files",
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Replicate file upload {exc.code}: {body_text[:400]}") from exc
    get_url = (payload.get("urls") or {}).get("get")
    if not get_url:
        raise RuntimeError(f"Replicate file upload missing urls.get: {payload}")
    return str(get_url)


def generate_replicate_image(
    prompt: str,
    out_path: Path,
    *,
    token: str,
    model: str = "[REDACTED]",
    aspect_ratio: str = "9:16",
) -> str:
    """Run Replicate model and save first output image to out_path."""
    if "/" not in model:
        raise ValueError(f"Invalid Replicate model slug: {model}")

    owner, name = model.split("/", 1)
    url = f"{API_BASE}/models/{owner}/{name}/predictions"
    body = {
        "input": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "num_outputs": 1,
            "output_format": "png",
            "go_fast": True,
        }
    }
    created = _request("POST", url, token=token, payload=body)
    pred_id = created.get("id")
    if not pred_id:
        raise RuntimeError(f"Replicate returned no prediction id: {created}")

    result = _poll_prediction(pred_id, token=token)
    output = result.get("output")
    if not output:
        raise RuntimeError(f"Replicate empty output: {result}")

    image_url = output[0] if isinstance(output, list) else output
    if not isinstance(image_url, str):
        raise RuntimeError(f"Unexpected Replicate output type: {type(output)}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _download_url(image_url, out_path)
    return f"replicate/{model}"


def generate_replicate_kling_video(
    prompt: str,
    out_path: Path,
    *,
    token: str,
    model: str = "kwaivgi/kling-v3-video",
    duration: int = 15,
    aspect_ratio: str = "9:16",
    mode: str = "pro",
    generate_audio: bool = True,
    multi_prompt: list[dict] | None = None,
    start_image_path: Path | None = None,
    negative_prompt: str = "",
    timeout_sec: int = 900,
) -> str:
    """Kling 3.0 text/image-to-video with optional native audio and multi-shot."""
    if "/" not in model:
        raise ValueError(f"Invalid Replicate Kling model slug: {model}")

    owner, name = model.split("/", 1)
    url = f"{API_BASE}/models/{owner}/{name}/predictions"
    body_input: dict = {
        "prompt": prompt,
        "duration": max(3, min(15, int(duration))),
        "aspect_ratio": aspect_ratio,
        "mode": mode,
        "generate_audio": bool(generate_audio),
    }
    if negative_prompt.strip():
        body_input["negative_prompt"] = negative_prompt.strip()
    if multi_prompt:
        body_input["multi_prompt"] = multi_prompt
    if start_image_path and start_image_path.exists():
        body_input["start_image"] = upload_replicate_file(start_image_path, token=token)

    body = {"input": body_input}
    created = _request("POST", url, token=token, payload=body)
    pred_id = created.get("id")
    if not pred_id:
        raise RuntimeError(f"Replicate Kling returned no prediction id: {created}")

    result = _poll_prediction(pred_id, token=token, timeout_sec=timeout_sec)
    output = result.get("output")
    if not output:
        raise RuntimeError(f"Replicate Kling empty output: {result}")

    video_url = output if isinstance(output, str) else (output[0] if isinstance(output, list) else None)
    if not isinstance(video_url, str):
        raise RuntimeError(f"Unexpected Replicate Kling output: {type(output)}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _download_url(video_url, out_path)
    return f"replicate/{model}"


def generate_replicate_i2v(
    prompt: str,
    image_path: Path,
    out_path: Path,
    *,
    token: str,
    model: str = "minimax/video-01",
    timeout_sec: int = 600,
) -> str:
    """Image-to-video clip (first frame = image, prompt = motion)."""
    if "/" not in model:
        raise ValueError(f"Invalid Replicate video model slug: {model}")

    image_url = upload_replicate_file(image_path, token=token)
    owner, name = model.split("/", 1)
    url = f"{API_BASE}/models/{owner}/{name}/predictions"
    body_input: dict = {
        "prompt": prompt,
        "first_frame_image": image_url,
        "prompt_optimizer": True,
    }
    if "hailuo" in model.lower():
        body_input["duration"] = 6
        body_input["resolution"] = "768p"
    body = {"input": body_input}
    created = _request("POST", url, token=token, payload=body)
    pred_id = created.get("id")
    if not pred_id:
        raise RuntimeError(f"Replicate video returned no prediction id: {created}")

    result = _poll_prediction(pred_id, token=token, timeout_sec=timeout_sec)
    output = result.get("output")
    if not output:
        raise RuntimeError(f"Replicate video empty output: {result}")

    video_url = output if isinstance(output, str) else (output[0] if isinstance(output, list) else None)
    if not isinstance(video_url, str):
        raise RuntimeError(f"Unexpected Replicate video output: {type(output)}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _download_url(video_url, out_path)
    return f"replicate/{model}"


def probe_replicate(token: str, model: str = "[REDACTED]") -> tuple[bool, str]:
    try:
        owner, name = model.split("/", 1)
        url = f"{API_BASE}/models/{owner}/{name}"
        _request("GET", url, token=token)
        return True, f"Replicate model {model} reachable"
    except Exception as exc:
        return False, str(exc)[:200]
