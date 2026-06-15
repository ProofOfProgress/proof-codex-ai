"""Tunable Blender render parameters — RL-style search space for micro jumpscare."""

from __future__ import annotations

import copy
import json
import random
import re
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any


@dataclass
class BlenderParams:
    """Knobs mapped to BLENDER_* env vars in build_and_render.py."""

    samples: int = 24
    camera_z: float = 2.18
    look_z: float = 1.72
    focal_mm: float = 26.0
    face_scale: float = 1.38
    mouth_emissive: float = 7.5
    mouth_red: float = 0.95
    rule_of_thirds: float = 2 / 3
    exposure: float = 0.65
    lunge_action_trim: str = "78,140"

    def to_env(self) -> dict[str, str]:
        return {
            "BLENDER_SAMPLES": str(int(self.samples)),
            "BLENDER_LUNGE_CAMERA_Z": f"{self.camera_z:.3f}",
            "BLENDER_LUNGE_LOOK_Z": f"{self.look_z:.3f}",
            "BLENDER_LUNGE_FOCAL_MM": f"{self.focal_mm:.1f}",
            "BLENDER_LUNGE_FACE_SCALE": f"{self.face_scale:.3f}",
            "BLENDER_MOUTH_EMISSIVE": f"{self.mouth_emissive:.2f}",
            "BLENDER_MOUTH_RED": f"{self.mouth_red:.3f}",
            "BLENDER_RULE_OF_THIRDS": f"{self.rule_of_thirds:.4f}",
            "BLENDER_EXPOSURE": f"{self.exposure:.3f}",
            "BLENDER_LUNGE_ACTION_TRIM": self.lunge_action_trim,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BlenderParams:
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})

    @classmethod
    def defaults(cls) -> BlenderParams:
        try:
            from shorts_bot.config import settings

            return cls(
                samples=max(16, min(48, settings.blender_self_train_samples)),
                camera_z=settings.blender_self_train_camera_z,
                rule_of_thirds=settings.micro_jumpscare_rule_of_thirds,
                mouth_emissive=settings.blender_self_train_mouth_emissive,
            )
        except Exception:
            return cls()

    def clamp(self) -> BlenderParams:
        p = copy.deepcopy(self)
        p.samples = int(max(16, min(64, p.samples)))
        p.camera_z = max(1.45, min(2.85, p.camera_z))
        p.look_z = max(1.2, min(2.2, p.look_z))
        p.focal_mm = max(18.0, min(42.0, p.focal_mm))
        p.face_scale = max(1.05, min(1.85, p.face_scale))
        p.mouth_emissive = max(2.0, min(16.0, p.mouth_emissive))
        p.mouth_red = max(0.7, min(1.0, p.mouth_red))
        p.rule_of_thirds = max(0.55, min(0.78, p.rule_of_thirds))
        p.exposure = max(0.25, min(0.85, p.exposure))
        return p

    def mutate(self, *, strength: float = 0.08, rng: random.Random | None = None) -> BlenderParams:
        """Small random walk — exploration between scored trials."""
        r = rng or random.Random()
        p = self.clamp()
        p.camera_z += r.uniform(-strength, strength) * 0.8
        p.look_z += r.uniform(-strength, strength) * 0.5
        p.focal_mm += r.uniform(-strength, strength) * 6.0
        p.face_scale += r.uniform(-strength, strength) * 0.25
        p.mouth_emissive += r.uniform(-strength, strength) * 2.0
        p.mouth_red += r.uniform(-strength, strength) * 0.08
        p.rule_of_thirds += r.uniform(-strength, strength) * 0.06
        p.exposure += r.uniform(-strength, strength) * 0.12
        if r.random() < 0.15:
            p.samples += r.choice([-4, 4, 8])
        return p.clamp()


_ISSUE_PATCHES: list[tuple[re.Pattern[str], dict[str, float | int]]] = [
    (re.compile(r"dark|underexpos|too black|can.t see", re.I), {"exposure": 0.08, "mouth_emissive": 1.2}),
    (re.compile(r"small|tiny|distant|far away|not close", re.I), {"face_scale": 0.1, "focal_mm": -2.0}),
    (re.compile(r"face|mouth|teeth|scream|open", re.I), {"face_scale": 0.06, "mouth_emissive": 1.0}),
    (re.compile(r"red|blood|gore|interior", re.I), {"mouth_emissive": 1.8, "mouth_red": 0.04}),
    (re.compile(r"low angle|looking up|camera too low", re.I), {"camera_z": 0.14, "look_z": 0.06}),
    (re.compile(r"high angle|looking down|camera too high", re.I), {"camera_z": -0.12, "look_z": -0.05}),
    (re.compile(r"blur|soft|noisy|grain", re.I), {"samples": 8}),
    (re.compile(r"grey|gray|block.?out|untextured|flat", re.I), {"samples": 6, "exposure": 0.06}),
    (re.compile(r"framing|thirds|eyes|composition", re.I), {"rule_of_thirds": 0.02}),
]


def patch_from_issues(params: BlenderParams, issues: list[str]) -> BlenderParams:
    """Exploit step — nudge params from Gemini vision QC issue text."""
    p = copy.deepcopy(params).clamp()
    blob = " ".join(issues).lower()
    if not blob.strip():
        return p
    for pattern, deltas in _ISSUE_PATCHES:
        if not pattern.search(blob):
            continue
        for key, delta in deltas.items():
            cur = getattr(p, key)
            if isinstance(cur, int):
                setattr(p, key, int(cur + delta))
            else:
                setattr(p, key, float(cur + delta))
    return p.clamp()


def save_params(path: Path, params: BlenderParams, *, meta: dict[str, Any] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"params": asdict(params.clamp()), "meta": meta or {}}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_params(path: Path) -> BlenderParams | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return BlenderParams.from_dict(data.get("params") or data)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None
