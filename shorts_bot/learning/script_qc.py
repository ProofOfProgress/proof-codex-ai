"""Legacy pre-InVideo script QC — RETIRED. Use shorts_bot.tiktok_shop.module1_qc."""

from __future__ import annotations

from dataclasses import dataclass

from shorts_bot.config import settings


@dataclass
class ScriptQCResult:
    passed: bool
    score: float
    issues: list[str]
    summary: str


def score_script_brief(
    *,
    product: str,
    hook: str,
    brief: str,
    verdict_hint: str = "",
) -> ScriptQCResult:
    """Retired — affiliate QC is Module 1 (`module1_qc.py`) + course modules 7–8."""
    if settings.script_qc_enabled:
        return ScriptQCResult(
            passed=False,
            score=0.0,
            issues=[
                "script_qc is retired; enable Module 1 QC via tiktok_shop and follow data/research/course/"
            ],
            summary="Use module1_qc + course modules",
        )
    return ScriptQCResult(passed=True, score=10.0, issues=[], summary="Legacy script QC disabled")
