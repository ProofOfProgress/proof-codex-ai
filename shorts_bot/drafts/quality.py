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
    "scary story #",
    "scary stories",
    "creepypasta",
    "hey guys",
    "welcome back",
]

COSY_PHRASES = [
    "self-care",
    "self help",
    "mental health",
    "one breath",
    "grounding",
    "cozy",
    "cosy",
    "warm lamp",
    "tea ritual",
    "you're still here",
    "protocol",
    "micro-win",
]

GENERIC_CREEPY_PHRASES = [
    "something scary",
    "very haunted",
    "super creepy",
    "ghost story",
    "urban legend",
]

FALSE_CALM_CUES = [
    "quiet",
    "still",
    "told yourself",
    "telling yourself",
    "maybe it was",
    "just a",
    "for a second",
    "held your breath",
    "nothing moved",
    "lag",
    "trick",
]

JUMPSCARE_CUES = [
    "turned",
    "looked",
    "blink",
    "door",
    "mirror",
    "closet",
    "screen",
    "behind you",
    "opened",
    "lunged",
    "scream",
    "face",
    "grab",
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
    if word_count < 50:
        issues.append(f"Script too short ({word_count} words). Aim for 70-110 for a horror Short.")
    elif word_count > 140:
        warnings.append(f"Script may be long for a horror Short ({word_count} words). Keep under ~35s.")

    if len(hook.strip()) < 12:
        issues.append("Hook is too weak — need a specific impossible detail in line 1.")

    if len(help_angle.strip()) < 20:
        issues.append("Scare angle is vague. Name scare type (reflection/knock/glitch/lunge) and the impossible hook.")

    lowered = script.lower()
    hook_lower = hook.lower()

    for phrase in SLOP_PHRASES:
        if phrase in lowered:
            issues.append(f"Slop phrase detected: '{phrase}'")

    for phrase in COSY_PHRASES:
        if phrase in lowered:
            issues.append(f"Cosy/self-help tone detected: '{phrase}' — use horror micro-story voice.")

    for phrase in GENERIC_CREEPY_PHRASES:
        if phrase in lowered:
            warnings.append(f"Generic horror framing: '{phrase}' — swap for a specific impossible detail.")

    if re.search(r"\b(i used to|this helped me|my therapist|same loop every night)\b", lowered):
        issues.append("Self-help first-person voice — use second-person 'you' horror micro-story.")

    from shorts_bot.config import settings
    from shorts_bot.production.jenny_checks import check_jenny_voice

    for issue in check_jenny_voice(script, hook):
        if settings.pipeline_block_voice_drift:
            issues.append(issue)
        else:
            warnings.append(issue)

    if not re.search(r"\byou\b", lowered):
        warnings.append("Missing singular 'you' — Don't Blink scripts are second-person micro-stories.")

    impossible_cues = (
        "blink",
        "reflection",
        "mirror",
        "timestamp",
        "delivered",
        "tomorrow",
        "yesterday",
        "inside",
        "muted",
        "heartbeat",
        "motion",
        "alone",
        "wrong",
        "impossible",
        "longer",
        "off",
        "empty",
        "future",
        "deleted",
    )
    if not any(c in hook_lower for c in impossible_cues):
        warnings.append(
            "Hook may lack an impossible detail — lead with timestamp/reflection/text/knock wrongness."
        )

    if not any(c in lowered for c in FALSE_CALM_CUES):
        msg = "No false-calm beat detected — add a quiet 'maybe it was nothing' moment before the scare."
        if settings.launch_quality_strict:
            issues.append(msg)
        else:
            warnings.append(msg)

    tail = lowered[-120:]
    if not any(c in tail for c in JUMPSCARE_CUES):
        warnings.append("Final lines may not cue a jumpscare — end on a visual scare trigger.")

    if not re.search(r"[.!?]", script):
        warnings.append("Script has no sentence endings. Add clearer pacing.")

    if topic.strip().lower() in {"", "tbd", "test"}:
        warnings.append("Topic looks placeholder-ish.")

    if re.search(r"watch the whole thing\.?\s*$", script.strip(), re.I):
        warnings.append("Script ends with channel tagline — cut it; end on the jumpscare cue instead.")

    if re.search(r"stick figure", lowered):
        issues.append("Stick figures are banned — use cinematic horror visual beats.")

    return QualityReport(passed=len(issues) == 0, issues=issues, warnings=warnings)
