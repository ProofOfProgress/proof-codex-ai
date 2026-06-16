"""Gemini vision QC loop for Lost Boy Recraft stills — retry until composition passes."""

from __future__ import annotations

import base64
import json
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

from shorts_bot.config import settings
from shorts_bot.production.images.recraft import generate_recraft_image


def _gemini_review_image(
    image_path: Path,
    *,
    requirements: str,
    spoken_line: str,
) -> tuple[bool, str, str]:
    """Return (passed, issues, revised_prompt_hint)."""
    if not settings.has_gemini:
        return True, "", ""

    im = Image.open(image_path).convert("RGB")
    buf = BytesIO()
    im.save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode()

    model = (settings.gemini_vision_model or settings.gemini_model or "gemini-2.5-flash-lite").strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.gemini_api_key}"
    prompt = f"""You QC horror Short keyframes for a Lost Boy series.

Spoken line for this frame: "{spoken_line}"

Requirements:
{requirements}

Reply JSON only:
{{"pass": true/false, "issues": "short", "prompt_fix": "one sentence to add to image prompt if fail"}}

Pass if composition matches requirements. Fail if wrong pose, wrong character count, or same generic solo monster again when group shot needed."""

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/jpeg", "data": b64}},
                ]
            }
        ]
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        raw = json.loads(resp.read())["candidates"][0]["content"]["parts"][0]["text"]

    text = raw.strip()
    if "```" in text:
        text = text.split("```")[1].replace("json", "").strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return True, "", ""
    passed = bool(data.get("pass"))
    issues = str(data.get("issues") or "")
    fix = str(data.get("prompt_fix") or "")
    return passed, issues, fix


def generate_still_with_qc(
    prompt: str,
    out_path: Path,
    *,
    style_id: str | None,
    spoken_line: str,
    requirements: str,
    max_attempts: int = 3,
) -> bool:
    """Generate Recraft still; retry with Gemini prompt fixes up to max_attempts."""
    api_key = settings.recraft_api_key or ""
    current = prompt
    out_path.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, max_attempts + 1):
        try:
            generate_recraft_image(
                current,
                out_path,
                api_key=api_key,
                model=settings.recraft_model,
                style_id=style_id,
                size=settings.recraft_image_size,
            )
        except Exception as exc:
            if "content filter" in str(exc).lower() or "prompt_is_improper" in str(exc).lower():
                current = (
                    f"{prompt} SAFE: family-friendly horror illustration, no harm, "
                    "cartoon forest scene, unsettling but not violent."
                )
                if attempt >= max_attempts:
                    return False
                continue
            raise
        passed, issues, fix = _gemini_review_image(
            out_path,
            requirements=requirements,
            spoken_line=spoken_line,
        )
        if passed:
            return True
        if fix and attempt < max_attempts:
            current = f"{prompt} FIX: {fix} Previous issues: {issues}"
    return out_path.is_file() and out_path.stat().st_size > 1000
