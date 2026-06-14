"""Motion for Blender clips — Proscenium FBX exports preferred over procedural fallback.

Backends:
  proscenium_fbx — use owner FBX from channel/assets/motion_exports/ (Proscenium addon)
  procedural     — built-in wave/lunge until Proscenium export exists
  kimodo         — NVIDIA text-to-motion (needs local NVIDIA GPU; stub until wired)

Gemini/Cursor bone guessing is disabled — use Proscenium in Blender 5 (see docs/FOR_OWNER_PROSCENIUM.md).
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from shorts_bot.config import settings

PHASES = ("open", "wave", "lunge")

# SCP-096 / humanoid rig bones we allow the model to rotate
DEFAULT_BONES = (
    "pelvis",
    "ripcage",
    "neck",
    "head",
    "Bone_007",
    "Bone_009",
    "Bone_012",
    "Bone_011",
    "Bone_008",
    "Bone_010",
    "Bone_014",
    "Bone_013",
)

PHASE_DEFAULT_PROMPTS: dict[str, str] = {
    "open": "Figure emerges from fog — slow stiff walk toward camera, shoulders wrong, head too still.",
    "wave": "Slow uncanny wave with right arm — arm rises, wrist bent backward, not friendly, head tilts toward viewer.",
    "lunge": "Horror jumpscare lunge — torso and neck snap forward toward camera, arms reach out, last 0.5 seconds explosive.",
}

# Procedural fallback (matches build_and_render.py wave chain)
PROCEDURAL_WAVE: list[tuple[float, dict[str, tuple[float, float, float]]]] = [
    (0.05, {"Bone_007": (0, 0, 0), "Bone_009": (0, 0, 0), "Bone_012": (0, 0, 0), "Bone_011": (0, 0, 0)}),
    (0.20, {"Bone_007": (-1.4, 0.15, -0.25), "Bone_009": (-0.4, 0, 0.1), "Bone_012": (0.3, 0, 0.5), "Bone_011": (0, 0, 0.6)}),
    (0.38, {"Bone_007": (-2.0, 0.2, -0.35), "Bone_009": (-0.9, 0.1, -0.15), "Bone_012": (0.5, 0.15, 0.9), "Bone_011": (0.2, 0, 1.1)}),
    (0.52, {"Bone_007": (-2.15, 0.18, -0.3), "Bone_009": (-1.0, 0.08, -0.2), "Bone_012": (0.45, 0.1, 1.0), "Bone_011": (0.15, 0, 1.2)}),
    (0.65, {"Bone_007": (-1.85, 0.12, -0.28), "Bone_009": (-0.75, 0, 0.05), "Bone_012": (0.35, 0, 0.75), "Bone_011": (0, 0, 0.9)}),
    (0.78, {"Bone_007": (-2.05, 0.16, -0.32), "Bone_009": (-0.95, 0.06, -0.1), "Bone_012": (0.4, 0.08, 0.95), "Bone_011": (0.1, 0, 1.05)}),
    (0.92, {"Bone_007": (-1.6, 0.1, -0.2), "Bone_009": (-0.5, 0, 0), "Bone_012": (0.2, 0, 0.4), "Bone_011": (0, 0, 0.5)}),
]

PROCEDURAL_LUNGE: list[tuple[float, dict[str, tuple[float, float, float]]]] = [
    (0.0, {"pelvis": (0, 0, 0), "ripcage": (0, 0, 0), "neck": (0, 0, 0), "head": (0, 0, 0)}),
    (0.75, {"ripcage": (0.15, 0, 0), "neck": (0.2, 0, 0), "head": (0.1, 0, 0)}),
    (1.0, {"ripcage": (0.5, 0, 0), "neck": (0.45, 0, 0), "head": (0.35, 0, 0), "Bone_007": (-2.2, 0, 0)}),
]


def motion_cache_path(pack_dir: Path, phase: str) -> Path:
    return pack_dir / f"motion_{phase}.json"


def _clamp_rot(val: float) -> float:
    return max(-math.pi, min(math.pi, float(val)))


def _sanitize_keyframes(raw: Any, *, phase: str) -> list[dict[str, Any]]:
    """Validate LLM JSON — fractions 0..1, known bones, clamped euler radians."""
    if not isinstance(raw, dict):
        raise ValueError("motion JSON must be an object")
    frames = raw.get("keyframes")
    if not isinstance(frames, list) or len(frames) < 2:
        raise ValueError("need at least 2 keyframes")
    allowed = set(DEFAULT_BONES)
    out: list[dict[str, Any]] = []
    for item in frames:
        if not isinstance(item, dict):
            continue
        t = float(item.get("t", item.get("frac", 0)))
        t = max(0.0, min(1.0, t))
        bones_in = item.get("bones") or {}
        if not isinstance(bones_in, dict):
            continue
        bones: dict[str, list[float]] = {}
        for name, rot in bones_in.items():
            if name not in allowed:
                continue
            if not isinstance(rot, (list, tuple)) or len(rot) != 3:
                continue
            bones[name] = [_clamp_rot(rot[0]), _clamp_rot(rot[1]), _clamp_rot(rot[2])]
        if bones:
            out.append({"t": t, "bones": bones})
    out.sort(key=lambda x: x["t"])
    if len(out) < 2:
        raise ValueError("too few valid bone keyframes after sanitize")
    return out


def _procedural_keyframes(phase: str) -> list[dict[str, Any]]:
    src = PROCEDURAL_WAVE if phase == "wave" else PROCEDURAL_LUNGE if phase == "lunge" else []
    if phase == "open":
        return [
            {"t": 0.0, "bones": {"pelvis": [0, 0, 0], "ripcage": [0, 0, 0]}},
            {"t": 1.0, "bones": {"pelvis": [0.05, 0, 0], "ripcage": [0.08, 0, 0], "neck": [0.05, 0, 0]}},
        ]
    return [{"t": t, "bones": {k: list(v) for k, v in bones.items()}} for t, bones in src]


def _gemini_motion_keyframes(prompt: str, *, phase: str) -> list[dict[str, Any]]:
    from shorts_bot.llm.provider import get_llm_backend

    backend = get_llm_backend()
    if not backend:
        raise RuntimeError("GEMINI_API_KEY or OPENAI_API_KEY required for gemini motion backend")

    bone_list = ", ".join(DEFAULT_BONES)
    system = (
        "You output ONLY valid JSON for Blender armature pose animation. "
        "Rotation values are XYZ euler radians. Horror / uncanny motion — not cartoon. "
        "Use 5-9 keyframes with t from 0.0 to 1.0 (fraction of clip duration)."
    )
    user = (
        f"Phase: {phase}\n"
        f"Motion description: {prompt}\n\n"
        f"Allowed bones: {bone_list}\n\n"
        "Return JSON exactly like:\n"
        '{"keyframes":[{"t":0.0,"bones":{"Bone_007":[0,0,0]}},{"t":0.5,"bones":{"Bone_007":[-2.0,0.2,-0.3]}}]}\n'
        "Right arm chain for wave: Bone_007 → Bone_009 → Bone_012 → Bone_011."
    )
    resp = backend.client.chat.completions.create(
        model=backend.model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
        max_tokens=2048,
        response_format={"type": "json_object"},
    )
    text = (resp.choices[0].message.content or "").strip()
    if "```" in text:
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise
        data = json.loads(match.group(0))
    return _sanitize_keyframes(data, phase=phase)


def _kimodo_motion_keyframes(prompt: str, *, phase: str) -> list[dict[str, Any]]:
    raise RuntimeError(
        "Kimodo backend needs an NVIDIA GPU on the render machine. "
        "Install: https://github.com/nv-tlabs/kimodo — then set BLENDER_MOTION_BACKEND=kimodo. "
        "Until then use BLENDER_MOTION_BACKEND=gemini (describe motion in English)."
    )


def resolve_backend() -> str:
    raw = (settings.blender_motion_backend or "procedural").strip().lower()
    if raw in ("auto", "gemini"):
        return "procedural"
    return raw


def _proscenium_fbx_available(draft_id: int, phase: str) -> bool:
    from shorts_bot.production.blender.motion_exports import resolve_motion_fbx

    return resolve_motion_fbx(draft_id, phase) is not None


def generate_motion_keyframes(
    prompt: str,
    *,
    phase: str,
    backend: str | None = None,
) -> dict[str, Any]:
    """Turn English motion description into sanitized keyframe list."""
    phase = phase if phase in PHASES else "wave"
    bk = (backend or resolve_backend()).lower()
    try:
        if bk == "gemini":
            keyframes = _gemini_motion_keyframes(prompt, phase=phase)
            source = "gemini"
        elif bk == "kimodo":
            keyframes = _kimodo_motion_keyframes(prompt, phase=phase)
            source = "kimodo"
        else:
            keyframes = _procedural_keyframes(phase)
            source = "procedural"
    except Exception as exc:
        keyframes = _procedural_keyframes(phase)
        source = f"procedural_fallback ({exc.__class__.__name__})"

    return {
        "phase": phase,
        "prompt": prompt,
        "backend": source,
        "keyframes": keyframes,
    }


def load_beat_prompt(draft_id: int, phase: str) -> str:
    """Pull motion text from draft beat sheet for open / wave / lunge clip."""
    meta_path = settings.data_dir / "draft_meta" / f"draft_{draft_id}.json"
    if not meta_path.is_file():
        return PHASE_DEFAULT_PROMPTS.get(phase, PHASE_DEFAULT_PROMPTS["wave"])

    data = json.loads(meta_path.read_text(encoding="utf-8"))
    beats = data.get("beat_sheet") or []
    if not beats:
        return PHASE_DEFAULT_PROMPTS.get(phase, PHASE_DEFAULT_PROMPTS["wave"])

    phase_ranges = {
        "open": (0.0, 10.0),
        "wave": (10.0, 20.0),
        "lunge": (20.0, 30.0),
    }
    t0, t1 = phase_ranges.get(phase, (0.0, 10.0))
    lines: list[str] = []
    for beat in beats:
        start = float(beat.get("start_sec", 0))
        if t0 <= start < t1:
            vis = (beat.get("visual") or "").strip()
            cam = (beat.get("camera") or "").strip()
            if vis:
                lines.append(vis)
            if cam:
                lines.append(f"Camera: {cam}")
    if lines:
        return " ".join(lines)
    return PHASE_DEFAULT_PROMPTS.get(phase, PHASE_DEFAULT_PROMPTS["wave"])


def prepare_motion_for_pack(
    pack_dir: Path,
    draft_id: int,
    *,
    phases: tuple[str, ...] = PHASES,
    force: bool = False,
    prompt_override: str | None = None,
) -> dict[str, Path]:
    """Prepare motion sidecars before Blender render (Proscenium FBX marker or procedural JSON)."""
    from shorts_bot.production.blender.motion_exports import resolve_motion_fbx

    pack_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    bk = resolve_backend()

    for phase in phases:
        out = motion_cache_path(pack_dir, phase)
        fbx = resolve_motion_fbx(draft_id, phase)
        if fbx and bk in ("proscenium_fbx", "proscenium", "auto", "procedural"):
            payload = {
                "phase": phase,
                "backend": "proscenium_fbx",
                "source_fbx": str(fbx),
                "prompt": prompt_override or load_beat_prompt(draft_id, phase),
            }
            out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            written[phase] = out
            continue
        if out.is_file() and not force:
            written[phase] = out
            continue
        prompt = prompt_override or load_beat_prompt(draft_id, phase)
        payload = generate_motion_keyframes(prompt, phase=phase, backend=bk)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        written[phase] = out
    return written


def load_motion_keyframes(pack_dir: Path, phase: str) -> list[dict[str, Any]] | None:
    path = motion_cache_path(pack_dir, phase)
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    kf = data.get("keyframes")
    if isinstance(kf, list) and kf:
        return kf
    return None
