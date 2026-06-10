from __future__ import annotations

import re
from dataclasses import dataclass, field


SLOP_PHRASES = [
    "in today's fast-paced world",
    "game changer",
    "you won't believe",
    "let's dive in",
    "without further ado",
    "unlock your potential",
    "the ultimate guide",
    "here's the thing",
    "buckle up",
    "mind-blowing",
]

GENERIC_HELP_PHRASES = [
    "everyone",
    "anyone who wants to improve",
    "people everywhere",
    "all of us",
]


@dataclass
class QualityReport:
    passed: bool
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.passed and not self.warnings:
            return "Quality checks passed."
        lines = []
        if self.issues:
            lines.append("Issues: " + "; ".join(self.issues))
        if self.warnings:
            lines.append("Warnings: " + "; ".join(self.warnings))
        return " ".join(lines) if lines else "Quality checks passed."


def run_quality_checks(
    *,
    topic: str,
    script: str,
    hook: str,
    help_angle: str,
) -> QualityReport:
    issues: list[str] = []
    warnings: list[str] = []

    word_count = len(script.split())
    if word_count < 40:
        issues.append(f"Script too short ({word_count} words). Aim for 40-120 for a Short.")
    elif word_count > 180:
        warnings.append(f"Script may be long for a Short ({word_count} words).")

    if len(hook.strip()) < 8:
        issues.append("Hook is too weak or missing.")

    if len(help_angle.strip()) < 20:
        issues.append("Help angle is vague. Say who this helps and how.")

    lowered = script.lower()
    for phrase in SLOP_PHRASES:
        if phrase in lowered:
            issues.append(f"Slop phrase detected: '{phrase}'")

    help_lower = help_angle.lower()
    if any(p in help_lower for p in GENERIC_HELP_PHRASES) and len(help_angle) < 60:
        warnings.append("Help angle sounds generic. Be more specific about the audience.")

    if not re.search(r"[.!?]", script):
        warnings.append("Script has no sentence endings. Add clearer pacing.")

    if topic.strip().lower() in {"", "tbd", "test"}:
        warnings.append("Topic looks placeholder-ish.")

    if re.search(r"you'?re still here\.?\s*(good\.?)?\s*$", script.strip(), re.I):
        warnings.append(
            "Script ends with channel tagline — cut it; end on the protocol payoff instead."
        )

    try:
        from shorts_bot.production.jenny_checks import check_jenny_voice

        for msg in check_jenny_voice(script, hook):
            warnings.append(f"Jenny: {msg}")
    except ImportError:
        pass

    return QualityReport(passed=len(issues) == 0, issues=issues, warnings=warnings)
