"""Persist Blender render trials — param vector + vision score."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from shorts_bot.production.blender.params import BlenderParams


@dataclass
class BlenderTrial:
    trial_id: int
    params: BlenderParams
    score: float
    passed: bool
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    video_path: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trial_id": self.trial_id,
            "params": asdict(self.params),
            "score": self.score,
            "passed": self.passed,
            "issues": self.issues,
            "warnings": self.warnings,
            "video_path": self.video_path,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BlenderTrial:
        return cls(
            trial_id=int(data["trial_id"]),
            params=BlenderParams.from_dict(data.get("params") or {}),
            score=float(data.get("score", 0)),
            passed=bool(data.get("passed")),
            issues=list(data.get("issues") or []),
            warnings=list(data.get("warnings") or []),
            video_path=str(data.get("video_path") or ""),
            created_at=float(data.get("created_at") or time.time()),
        )


class BlenderTrialStore:
    def __init__(self, pack_dir: Path) -> None:
        self.root = pack_dir / "blender_rl"
        self.trials_path = self.root / "trials.jsonl"
        self.best_path = self.root / "best_params.json"

    def record(self, trial: BlenderTrial) -> None:
        prev_best = self.best()
        self.root.mkdir(parents=True, exist_ok=True)
        with self.trials_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(trial.to_dict()) + "\n")
        if prev_best is None or trial.score > prev_best.score:
            from shorts_bot.production.blender.params import save_params

            save_params(
                self.best_path,
                trial.params,
                meta={
                    "score": trial.score,
                    "passed": trial.passed,
                    "trial_id": trial.trial_id,
                    "issues": trial.issues[:5],
                },
            )

    def all_trials(self) -> list[BlenderTrial]:
        if not self.trials_path.is_file():
            return []
        out: list[BlenderTrial] = []
        for line in self.trials_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(BlenderTrial.from_dict(json.loads(line)))
            except (json.JSONDecodeError, TypeError, ValueError, KeyError):
                continue
        return out

    def best(self) -> BlenderTrial | None:
        trials = self.all_trials()
        return max(trials, key=lambda t: t.score) if trials else None

    def next_trial_id(self) -> int:
        trials = self.all_trials()
        return (max(t.trial_id for t in trials) + 1) if trials else 1
