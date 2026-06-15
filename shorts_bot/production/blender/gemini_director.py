"""Gemini visual director — actionable fix list after each Blender trial."""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from typing import Any

from shorts_bot.config import settings
from shorts_bot.production.blender.params import BlenderParams


def _parse_json(raw: str) -> dict[str, Any]:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    else:
        brace = re.search(r"\{.*\}", text, re.S)
        if brace:
            text = brace.group(0)
    return json.loads(text)


def ask_gemini_lunge_director(
    *,
    frame_paths: list[Path],
    issues: list[str],
    params: BlenderParams,
    score: float,
) -> dict[str, Any]:
    """
    Send QC frames + issues to Gemini; return structured director notes
    (framing, lighting, mouth, params to tweak).
    """
    from shorts_bot.llm.provider import get_llm_backend

    backend = get_llm_backend()
    if backend is None or backend.provider != "gemini":
        return {"skipped": True, "reason": "no Gemini"}

    model = (settings.gemini_vision_model or settings.gemini_model).strip()
    issue_blob = "; ".join(issues[:8]) if issues else "none yet"
    param_blob = json.dumps(params.clamp().__dict__, indent=0)

    prompt = (
        "You are the Blender horror director for Peripheral — 3s creature lunge jumpscare lab.\n"
        "Target: LIGHTS ARE OFF quality — final frame = open mouth + red interior FILLING the screen.\n"
        "NEVER frame crotch/pelvis/legs — eyes and mouth must dominate the peak frame.\n\n"
        f"Vision QC score: {score:.1f}/10. Issues: {issue_blob}\n"
        f"Current params: {param_blob}\n\n"
        "Study the frames (hook + peak). Return ONLY JSON:\n"
        "{\n"
        '  "summary": "one sentence",\n'
        '  "must_fix": ["max 5 actionable bullets"],\n'
        '  "param_deltas": {"camera_z": 0.0, "look_z": 0.0, "face_scale": 0.0, "mouth_emissive": 0.0, "exposure": 0.0, "stop_gap": 0.0, "creature_z": 0.0, "focal_mm": 0.0, "rule_of_thirds": 0.0},\n'
        '  "pass_next_trial": false\n'
        "}\n"
        "param_deltas = small nudges (+/-) on current params. "
        "For crotch/legs framing: INCREASE camera_z and look_z (positive deltas), DECREASE stop_gap (negative = closer)."
    )

    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for path in frame_paths[:3]:
        if path.is_file():
            b64 = base64.standard_b64encode(path.read_bytes()).decode("ascii")
            content.append(
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            )

    resp = backend.client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": content}],
        max_tokens=400,
        temperature=0.25,
    )
    raw = (resp.choices[0].message.content or "").strip()
    return _parse_json(raw)


def sanitize_director_deltas(deltas: dict[str, Any], issues: list[str]) -> dict[str, float]:
    """Fix common Gemini mistakes (e.g. lowering camera when crotch framed)."""
    blob = " ".join(issues).lower()
    out: dict[str, float] = {}
    for key, val in (deltas or {}).items():
        try:
            out[key] = float(val)
        except (TypeError, ValueError):
            continue
    if re.search(r"crotch|pelvis|legs|groin|lower body|between the legs", blob):
        if out.get("camera_z", 0) < 0:
            out["camera_z"] = abs(out["camera_z"])
        if out.get("look_z", 0) > 0:
            out["look_z"] = -abs(out["look_z"]) * 0.5
        out.setdefault("stop_gap", 0.15)
        out.setdefault("creature_z", -0.08)
        if out.get("stop_gap", 0) < 0:
            out["stop_gap"] = abs(out["stop_gap"])
        if out.get("creature_z", 0) > 0:
            out["creature_z"] = -out["creature_z"] * 0.5
    if re.search(r"tiny|distant|small|far away", blob):
        out.setdefault("stop_gap", -0.06)
    if re.search(r"dark|underexpos|black", blob):
        out.setdefault("exposure", 0.10)
        out.setdefault("mouth_emissive", 1.2)
    if re.search(r"mouth|red|scare|weak", blob):
        out.setdefault("mouth_emissive", 1.5)
        out.setdefault("mouth_red", 0.03)
    return out


def apply_director_deltas(params: BlenderParams, director: dict[str, Any], *, issues: list[str] | None = None) -> BlenderParams:
    """Merge Gemini param_deltas into BlenderParams (clamped)."""
    raw = director.get("param_deltas") or {}
    deltas = sanitize_director_deltas(raw if isinstance(raw, dict) else {}, issues or [])
    p = params.clamp()
    for key, delta in deltas.items():
        if not hasattr(p, key):
            continue
        cur = getattr(p, key)
        if isinstance(cur, int):
            setattr(p, key, int(cur + float(delta)))
        else:
            setattr(p, key, float(cur) + float(delta))
    return p.clamp()


def save_director_notes(path: Path, director: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(director, indent=2), encoding="utf-8")
