"""Preflight peak still — one cheap Blender frame before full micro jumpscare render."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console

from shorts_bot.config import settings
from shorts_bot.production.vision_qc import VisionQCReport, run_preflight_still_qc

console = Console()
BLENDER_SCRIPT = Path(__file__).resolve().parent / "build_and_render.py"


@dataclass
class PreflightResult:
    passed: bool
    score: float
    still_path: Path
    report: VisionQCReport | None = None
    skipped: bool = False
    issues: list[str] = field(default_factory=list)
    message: str = ""


class PreflightFailedError(RuntimeError):
    """Peak still failed QC — skip full animation render."""

    def __init__(self, result: PreflightResult):
        self.result = result
        super().__init__(result.message or f"Preflight failed ({result.score:.1f}/10)")


def _peak_time(seconds: float) -> float:
    return round(max(0.5, seconds - 0.35), 2)


def render_peak_still(
    draft_id: int,
    pack_dir: Path,
    *,
    seconds: float | None = None,
    samples: int | None = None,
    extra_env: dict[str, str] | None = None,
    use_mixamo: bool | None = None,
    force: bool = False,
) -> Path:
    """Blender background — one JPEG at jumpscare peak."""
    from shorts_bot.production.blender.download_creature import ensure_scp096_model
    from shorts_bot.production.blender.motion_backend import motion_env

    pack_dir.mkdir(parents=True, exist_ok=True)
    sec = seconds if seconds is not None else settings.micro_jumpscare_seconds
    smp = samples if samples is not None else settings.blender_preflight_samples
    still = pack_dir / "preflight" / "peak_still.jpg"

    if not force and still.is_file() and still.stat().st_size > 2000:
        return still

    try:
        ensure_scp096_model(force=False)
    except Exception as exc:
        console.print(f"[yellow]Creature download skipped: {exc}[/yellow]")

    cmd = [
        "blender",
        "--background",
        "--python",
        str(BLENDER_SCRIPT),
        "--",
        "--draft-id",
        str(draft_id),
        "--pack-dir",
        str(pack_dir),
        "--peak-still",
        "--seconds",
        str(sec),
        "--samples",
        str(smp),
    ]
    env = {
        **__import__("os").environ,
        "BLENDER_INCLUDE_CREATURE": "1",
        "BLENDER_MICRO_JUMPSCARE": "1",
        "BLENDER_CREATURE_ONLY": "1",
        "BLENDER_CREATURE_TARGET_HEIGHT": str(settings.micro_jumpscare_creature_height),
        "BLENDER_MICRO_CREATURE_SCALE": str(settings.micro_jumpscare_creature_scale),
        **motion_env(use_mixamo=use_mixamo),
    }
    if extra_env:
        env.update(extra_env)

    console.print(f"[cyan]Preflight still[/cyan] — draft #{draft_id} @ {smp} samples")
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if not still.is_file() or still.stat().st_size < 800:
        tail = (proc.stderr or proc.stdout or "")[-4000:]
        raise RuntimeError(f"Preflight still render failed:\n{tail}")
    if proc.returncode != 0:
        console.print("[yellow]Blender exited non-zero but still OK — continuing[/yellow]")
    return still


def run_preflight_gate(
    draft_id: int,
    pack_dir: Path,
    *,
    seconds: float | None = None,
    samples: int | None = None,
    extra_env: dict[str, str] | None = None,
    use_mixamo: bool | None = None,
    topic: str = "micro jumpscare lunge",
    hook: str = "creature lunge face fill",
    force_still: bool = True,
    min_score: float | None = None,
) -> PreflightResult:
    """
    Render peak still → Gemini QC → pass/fail.
    Caller skips full animation when passed is False.
    """
    if not settings.blender_preflight_still_enabled:
        return PreflightResult(
            passed=True,
            score=10.0,
            still_path=pack_dir / "preflight" / "peak_still.jpg",
            skipped=True,
            message="Preflight disabled",
        )

    sec = seconds if seconds is not None else settings.micro_jumpscare_seconds
    still = render_peak_still(
        draft_id,
        pack_dir,
        seconds=sec,
        samples=samples,
        extra_env=extra_env,
        use_mixamo=use_mixamo,
        force=force_still,
    )
    report = run_preflight_still_qc(
        still,
        pack_dir,
        topic=topic,
        hook=hook,
        peak_time=_peak_time(sec),
        min_score=min_score,
    )
    msg = f"Preflight {'PASS' if report.passed else 'FAIL'} {report.score:.1f}/10 — {still.name}"
    if report.issues:
        msg += " — " + "; ".join(report.issues[:2])
    console.print(f"[{'green' if report.passed else 'yellow'}]{msg}[/]")
    return PreflightResult(
        passed=report.passed,
        score=float(report.score),
        still_path=still,
        report=report,
        issues=list(report.issues),
        message=msg,
    )
