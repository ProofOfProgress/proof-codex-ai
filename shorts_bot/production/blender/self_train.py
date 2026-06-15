"""Blender self-reinforcement loop — render → vision score → param update → repeat."""

from __future__ import annotations

import random
import shutil
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.blender.params import (
    BlenderParams,
    load_params,
    patch_from_issues,
    save_params,
)
from shorts_bot.production.blender.trials import BlenderTrial, BlenderTrialStore
from shorts_bot.production.vision_qc import run_vision_qc

console = Console()


@dataclass
class BlenderSelfTrainResult:
    draft_id: int
    trials_run: int
    best_score: float
    best_passed: bool
    best_params: BlenderParams
    best_video: Path
    message: str


def _score_trial(report) -> float:
    """Numeric reward — vision QC score with small pass bonus."""
    bonus = 0.25 if report.passed else 0.0
    return float(report.score) + bonus


def _pick_next_params(
    *,
    best: BlenderTrial | None,
    last: BlenderTrial | None,
    rng: random.Random,
) -> BlenderParams:
    if best is None:
        saved = load_params(Path(settings.data_dir) / "production" / "blender_rl_defaults.json")
        return (saved or BlenderParams.defaults()).clamp()
    if last and last.issues:
        exploited = patch_from_issues(best.params, last.issues)
        return exploited.mutate(strength=0.04, rng=rng)
    return best.params.mutate(strength=0.07, rng=rng)


def run_blender_self_train(
    draft_id: int,
    *,
    pack_dir: Path | None = None,
    trials: int | None = None,
    target_score: float | None = None,
    topic: str = "micro jumpscare lunge",
    hook: str = "creature lunge face fill",
    force_render: bool = True,
) -> BlenderSelfTrainResult:
    """
    RL-style loop for Blender micro jumpscare:
    try params → render → Gemini vision QC → patch/mutate → repeat.
    Best params saved to pack_dir/blender_rl/best_params.json.
    """
    from shorts_bot.production.blender.micro_jumpscare_cli import produce_micro_jumpscare

    pack = pack_dir or (settings.data_dir / "production" / f"draft_{draft_id}")
    pack.mkdir(parents=True, exist_ok=True)
    store = BlenderTrialStore(pack)
    n_trials = trials if trials is not None else settings.blender_self_train_trials
    target = target_score if target_score is not None else settings.blender_self_train_target_score
    rng = random.Random(draft_id * 997 + n_trials)

    best_overall: BlenderTrial | None = store.best()
    last_trial: BlenderTrial | None = None

    console.print(
        f"[cyan]Blender self-train — draft #{draft_id}, {n_trials} trial(s), "
        f"target {target:.1f}/10[/cyan]"
    )

    for _ in range(n_trials):
        trial_id = store.next_trial_id()
        params = _pick_next_params(best=best_overall, last=last_trial, rng=rng)
        trial_dir = store.root / f"trial_{trial_id:03d}"
        trial_dir.mkdir(parents=True, exist_ok=True)

        console.print(
            f"[dim]Trial {trial_id}[/dim] cam_z={params.camera_z:.2f} "
            f"face={params.face_scale:.2f} mouth={params.mouth_emissive:.1f}"
        )

        produce_micro_jumpscare(
            draft_id,
            pack_dir=trial_dir,
            force=force_render,
            samples=params.samples,
            extra_env=params.to_env(),
        )
        video = trial_dir / "final_short.mp4"
        if not video.is_file():
            raise RuntimeError(f"Trial {trial_id} produced no video: {video}")

        report = run_vision_qc(
            video,
            trial_dir,
            topic=topic,
            hook=hook,
            use_cache=False,
        )
        reward = _score_trial(report)
        trial = BlenderTrial(
            trial_id=trial_id,
            params=params,
            score=reward,
            passed=report.passed,
            issues=list(report.issues),
            warnings=list(report.warnings),
            video_path=str(video),
        )
        store.record(trial)
        last_trial = trial
        if best_overall is None or trial.score > best_overall.score:
            best_overall = trial
            console.print(f"[green]New best[/green] {reward:.2f}/10 — {report.summary()}")
        else:
            console.print(f"[yellow]Score {reward:.2f}[/yellow] — {report.summary()}")

        if best_overall.score >= target:
            console.print(f"[green]Target {target:.1f} reached — stopping early[/green]")
            break

    assert best_overall is not None
    best_video = Path(best_overall.video_path)
    canonical = pack / "final_short.mp4"
    shutil.copy2(best_video, canonical)
    best_clip = pack / "clips" / "blender_part_01.mp4"
    best_clip.parent.mkdir(parents=True, exist_ok=True)
    src_clip = best_video.parent / "clips" / "blender_part_01.mp4"
    if src_clip.is_file():
        shutil.copy2(src_clip, best_clip)

    save_params(
        store.best_path,
        best_overall.params,
        meta={"score": best_overall.score, "trial_id": best_overall.trial_id},
    )

    if settings.self_training_enabled:
        try:
            from shorts_bot.learning.reflect import reflect_after_blender_rl
            from shorts_bot.memory.extensions import MemoryExtensions
            from shorts_bot.memory.store import MemoryStore

            mem = MemoryExtensions(MemoryStore(settings.database_path))
            reflect_after_blender_rl(
                mem,
                draft_id=draft_id,
                score=best_overall.score,
                passed=best_overall.passed,
                params=best_overall.params,
                issues=best_overall.issues,
            )
        except Exception as exc:
            console.print(f"[yellow]Self-training memory skip: {exc}[/yellow]")

    msg = (
        f"Blender self-train done — best {best_overall.score:.2f}/10 "
        f"(trial {best_overall.trial_id}) → {canonical.name}"
    )
    return BlenderSelfTrainResult(
        draft_id=draft_id,
        trials_run=len(store.all_trials()),
        best_score=best_overall.score,
        best_passed=best_overall.passed,
        best_params=best_overall.params,
        best_video=canonical,
        message=msg,
    )
