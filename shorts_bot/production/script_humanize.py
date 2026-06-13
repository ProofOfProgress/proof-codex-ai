"""Multi-pass AI detection + humanize before finalizing scripts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from shorts_bot.config import settings
from shorts_bot.production.jenny_checks import HORROR_SCRIPT_RULES, check_jenny_voice, jenny_retention_guidance
from shorts_bot.production.scene_plan import ai_likelihood_score


@dataclass
class ScriptFinalizeResult:
    hook: str
    script: str
    help_angle: str
    passes: int
    final_ai_score: int
    scores_log: list[int]
    message: str
    passed: bool

    @property
    def ok(self) -> bool:
        return self.passed


_HUMANIZE_PROMPT = """Rewrite this Peripheral horror YouTube Short script so it reads human-spoken, not AI-generated.

Target: **under 5% AI detection** (local score must be ≤5 on a 0–100 scale where 0 = human, 100 = obvious bot).

{horror_rules}

{retention}

Humanization rules:
- Keep second-person immersive voice (you/your) — NOT first-person vlog (I/my)
- Use contractions (don't, you're, it's, can't) — at least 3 in the script
- Vary sentence length — mix short punches with one longer line; no uniform rhythm
- No em dashes (—); use commas or periods
- No AI words: delve, tapestry, furthermore, unlock, navigate, landscape, moreover, in conclusion
- Keep same scare story beats — don't add steps or explain the ending
- Return JSON only: {{"hook": "...", "script": "...", "help_angle": "..."}}
"""


def _humanize_system_prompt(topic: str) -> str:
    return _HUMANIZE_PROMPT.format(
        horror_rules=HORROR_SCRIPT_RULES.strip(),
        retention=jenny_retention_guidance(topic),
    )


def _rule_humanize(text: str) -> str:
    t = text
    swaps = {
        " — ": ", ",
        "—": ", ",
        "Do not": "Don't",
        "do not": "don't",
        "It is": "It's",
        "it is": "it's",
        "You are": "You're",
        "you are": "you're",
        "cannot": "can't",
        "will not": "won't",
        "I live alone": "you live alone",
        "I pulled up": "you pulled up",
        "I tried to tell myself": "you told yourself",
        "My security camera": "Your security camera",
        "my security camera": "your security camera",
        "My heart": "Your chest",
        "my heart": "your chest",
    }
    for a, b in swaps.items():
        t = t.replace(a, b)
    t = re.sub(r"\bIn conclusion,?\s*", "", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _coerce_spoken_script(value) -> str:
    """Accept LLM mistakes like [{"spoken_text": "..."}] but keep VO plain text only."""
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict):
                spoken = item.get("spoken_text") or item.get("text") or item.get("line")
                if spoken:
                    parts.append(str(spoken).strip())
            elif item:
                parts.append(str(item).strip())
        return _rule_humanize(" ".join(p for p in parts if p))
    if isinstance(value, dict):
        for key in ("script", "spoken_text", "text", "line"):
            if key in value:
                return _coerce_spoken_script(value[key])
        return ""
    text = str(value or "").strip()
    if text.startswith(("[", "{")):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return _rule_humanize(text)
        coerced = _coerce_spoken_script(parsed)
        return coerced or _rule_humanize(text)
    return _rule_humanize(text)


def _llm_humanize(topic: str, hook: str, script: str, help_angle: str) -> dict[str, str] | None:
    from shorts_bot.llm.provider import get_llm_backend

    backend = get_llm_backend()
    if backend is None:
        return None
    payload = json.dumps({"topic": topic, "hook": hook, "script": script, "help_angle": help_angle})
    try:
        r = backend.client.chat.completions.create(
            model=backend.model,
            messages=[
                {"role": "system", "content": _humanize_system_prompt(topic)},
                {"role": "user", "content": payload},
            ],
            response_format={"type": "json_object"},
            temperature=0.9,
            max_tokens=800,
        )
        data = json.loads(r.choices[0].message.content or "{}")
        clean_script = _coerce_spoken_script(data.get("script"))
        if data.get("hook") and clean_script:
            return {
                "hook": str(data["hook"]).strip(),
                "script": clean_script,
                "help_angle": str(data.get("help_angle", help_angle)).strip(),
            }
    except Exception:
        return None
    return None


def finalize_script(
    topic: str,
    hook: str,
    script: str,
    help_angle: str,
    *,
    max_passes: int | None = None,
    threshold: int | None = None,
) -> ScriptFinalizeResult:
    """
    Run AI detector after each humanize pass until score <= threshold or max_passes.
    Default threshold 5 ≈ under 5% AI likelihood (heuristic 0–100 scale).
    """
    max_passes = max_passes or settings.ai_detect_max_passes
    threshold = threshold if threshold is not None else settings.ai_detect_threshold

    scores_log: list[int] = []
    h, s, ha = hook, script, help_angle
    rewrite_passes = 0

    for n in range(1, max_passes + 1):
        score = ai_likelihood_score(f"{h}\n{s}")
        jenny_issues = check_jenny_voice(s, h)
        scores_log.append(score)
        if score <= threshold and not jenny_issues:
            break
        llm = _llm_humanize(topic, h, s, ha)
        if llm:
            h, s, ha = llm["hook"], llm["script"], llm["help_angle"]
        else:
            h = _rule_humanize(h)
            s = _rule_humanize(s)
        rewrite_passes += 1

    final_score = ai_likelihood_score(f"{h}\n{s}")
    if not scores_log or scores_log[-1] != final_score:
        scores_log.append(final_score)
    jenny_issues = check_jenny_voice(s, h)
    passed = final_score <= threshold and not jenny_issues

    pct = final_score
    msg = (
        f"Script finalized after {rewrite_passes} humanize pass(es), "
        f"{len(scores_log)} detector read(s). "
        f"AI score {final_score}/100 (target ≤{threshold}, ~{pct}% AI likelihood). "
        f"Log: {scores_log}"
    )
    if not passed:
        extra = []
        if final_score > threshold:
            extra.append(f"score {final_score} > {threshold}")
        if jenny_issues:
            extra.append("voice drift: " + "; ".join(jenny_issues[:2]))
        msg += " — FAILED: " + ", ".join(extra)

    return ScriptFinalizeResult(
        hook=h,
        script=s,
        help_angle=ha,
        passes=rewrite_passes,
        final_ai_score=final_score,
        scores_log=scores_log,
        message=msg,
        passed=passed,
    )
