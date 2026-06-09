"""Multi-pass AI detection + humanize before finalizing scripts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from shorts_bot.config import settings
from shorts_bot.production.jenny_checks import check_jenny_voice
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


_HUMANIZE_PROMPT = """Rewrite this faceless YouTube Short using Jenny Hoyos course rules + personal creator voice.

VOICE: Real person making faceless videos — SAME struggles as viewer, sharing what helped THEM.
- First person: I, my, I used to, this helped me
- Singular "you" — never "hey guys"
- Contractions, mixed sentence lengths

JENNY STRUCTURE:
- Hook ASAP — curiosity + reason to watch to end
- Every line moves toward payoff; but/so momentum
- Payoff = best beat, then stop
- 3-5 mute-safe visual beats implied in script

Rules:
- No AI words: delve, tapestry, furthermore, unlock, navigate
- Keep same advice — don't add steps
- Return JSON only: {"hook": "...", "script": "...", "help_angle": "..."}
"""


def _rule_humanize(text: str) -> str:
    t = text
    swaps = {
        " — ": ", ",
        "Do not": "Don't",
        "do not": "don't",
        "It is": "It's",
        "it is": "it's",
        "You are": "You're",
        "you are": "you're",
        "cannot": "can't",
        "will not": "won't",
    }
    for a, b in swaps.items():
        t = t.replace(a, b)
    t = re.sub(r"\bIn conclusion,?\s*", "", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip()
    return t


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
                {"role": "system", "content": _HUMANIZE_PROMPT},
                {"role": "user", "content": payload},
            ],
            response_format={"type": "json_object"},
            temperature=0.9,
            max_tokens=800,
        )
        data = json.loads(r.choices[0].message.content or "{}")
        if data.get("hook") and data.get("script"):
            return {
                "hook": str(data["hook"]).strip(),
                "script": str(data["script"]).strip(),
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
    """
    max_passes = max_passes or settings.ai_detect_max_passes
    threshold = threshold if threshold is not None else settings.ai_detect_threshold

    scores_log: list[int] = []
    h, s, ha = hook, script, help_angle

    for n in range(1, max_passes + 1):
        score = ai_likelihood_score(s)
        jenny_issues = check_jenny_voice(s, h)
        scores_log.append(score)
        if score <= threshold and not jenny_issues:
            break
        llm = _llm_humanize(topic, h, s, ha)
        if llm:
            h, s, ha = llm["hook"], llm["script"], llm["help_angle"]
        else:
            s = _rule_humanize(s)
            h = _rule_humanize(h)

    final_score = ai_likelihood_score(s)
    scores_log.append(final_score)

    return ScriptFinalizeResult(
        hook=h,
        script=s,
        help_angle=ha,
        passes=len(scores_log),
        final_ai_score=final_score,
        scores_log=scores_log,
        message=(
            f"Script finalized after {len(scores_log)} detector pass(es). "
            f"AI score {final_score}/100 (target ≤{threshold}). "
            f"Log: {scores_log}"
        ),
    )
