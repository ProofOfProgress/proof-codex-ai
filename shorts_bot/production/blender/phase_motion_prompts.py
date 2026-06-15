"""Beat-sheet motion prompts — English for AI motion + Mixamo search keywords."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shorts_bot.config import settings

PHASES = ("open", "wave", "lunge")

# Curated per-draft: full English prompt + Mixamo keyword search
DRAFT_MOTION: dict[int, dict[str, dict[str, str]]] = {
    2: {
        "open": {
            "english": (
                "Form 2 rural horror — too-tall figure emerges from pine fog at gas station edge. "
                "Stiff wrong walk toward camera, shoulders too high, head too still. "
                "Teleports one hop closer when streetlight flickers off. Not human gait."
            ),
            "mixamo_query": "zombie walk",
            "notes": "Clip 1 — establish dread, 0–10s",
        },
        "wave": {
            "english": (
                "Slow uncanny wave with right arm — wrist bent backward, not friendly. "
                "Figure frozen between pumps while light is on; arm rises wrong, joints inverted. "
                "Horror uncanny valley, not a greeting."
            ),
            "mixamo_query": "waving",
            "notes": "Clip 2 — creepy wave beat, 10–20s",
        },
        "lunge": {
            "english": (
                "Horror jumpscare lunge — entity snaps from arm's length to lens in under 1 second. "
                "Torso and arms explode forward toward camera, still mid-wave. Hard stop at impact frame."
            ),
            "mixamo_query": "zombie attack",
            "notes": "Clip 3 — finale lunge, 20–30s",
        },
    },
}


def motion_config_path(draft_id: int) -> Path:
    return settings.data_dir / "draft_meta" / f"draft_{draft_id}_motion.json"


def load_phase_motion(draft_id: int, phase: str) -> dict[str, str]:
    """English prompt + mixamo_query for a clip phase."""
    phase = phase if phase in PHASES else "wave"
    path = motion_config_path(draft_id)
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        phases = data.get("phases") or {}
        if phase in phases and isinstance(phases[phase], dict):
            return phases[phase]
    return DRAFT_MOTION.get(draft_id, {}).get(phase, {})


def english_prompt(draft_id: int, phase: str) -> str:
    hit = load_phase_motion(draft_id, phase)
    if hit.get("english"):
        return str(hit["english"])
    from shorts_bot.production.blender.motion_prompt import load_beat_prompt

    return load_beat_prompt(draft_id, phase)


def mixamo_query(draft_id: int, phase: str) -> str:
    hit = load_phase_motion(draft_id, phase)
    if hit.get("mixamo_query"):
        return str(hit["mixamo_query"])
    defaults = {"open": "zombie walk", "wave": "waving", "lunge": "zombie attack"}
    return defaults.get(phase, "zombie walk")


def phase_queries_for_draft(draft_id: int) -> dict[str, str]:
    return all_phase_queries(draft_id)


def all_phase_queries(draft_id: int) -> dict[str, str]:
    return {p: mixamo_query(draft_id, p) for p in PHASES}


def export_motion_prompts_file(draft_id: int, pack_dir: Path) -> Path:
    """Write MOTION_PROMPTS.md + motion_prompts.json into production pack."""
    pack_dir.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {"draft_id": draft_id, "phases": {}}
    lines = [
        f"# Draft #{draft_id} — motion prompts",
        "",
        "Use **english** in Proscenium / Uthana. Use **mixamo_query** in Mixamo search box.",
        "",
    ]
    for phase in PHASES:
        cfg = load_phase_motion(draft_id, phase)
        payload["phases"][phase] = {
            "english": english_prompt(draft_id, phase),
            "mixamo_query": mixamo_query(draft_id, phase),
            "notes": cfg.get("notes", ""),
        }
        lines.extend(
            [
                f"## {phase.upper()} ({cfg.get('notes', '')})",
                "",
                "**English (AI motion):**",
                f"> {payload['phases'][phase]['english']}",
                "",
                f"**Mixamo search:** `{payload['phases'][phase]['mixamo_query']}`",
                "",
            ]
        )
    json_path = pack_dir / "motion_prompts.json"
    md_path = pack_dir / "MOTION_PROMPTS.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def ensure_draft_motion_json(draft_id: int) -> Path:
    """Seed draft_{N}_motion.json from curated defaults if missing."""
    path = motion_config_path(draft_id)
    if path.is_file():
        return path
    if draft_id not in DRAFT_MOTION:
        return path
    payload = {"draft_id": draft_id, "phases": DRAFT_MOTION[draft_id]}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
