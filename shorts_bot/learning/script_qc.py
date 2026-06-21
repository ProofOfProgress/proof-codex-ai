"""Pre-InVideo script QC — Gemini when available, heuristics offline."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from shorts_bot.config import settings

_VERDICT_WORDS = re.compile(r"\b(Pay|Skip|Wait)\b", re.I)


@dataclass
class ScriptQCResult:
    passed: bool
    score: float
    issues: list[str]
    summary: str

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "score": round(self.score, 2),
            "issues": self.issues,
            "summary": self.summary,
        }


def _offline_qc(*, product: str, hook: str, brief: str, verdict_hint: str) -> ScriptQCResult:
    issues: list[str] = []
    score = 10.0
    if len(hook.split()) > 18:
        issues.append("Hook too long for Shorts opener")
        score -= 2
    if product.lower() not in hook.lower() and product.lower() not in brief.lower()[:200]:
        issues.append("Product name missing from hook/opening")
        score -= 2
    if not _VERDICT_WORDS.search(brief) and not _VERDICT_WORDS.search(verdict_hint):
        issues.append("Missing Pay/Skip/Wait verdict language")
        score -= 3
    if "horror" in brief.lower() or "jumpscare" in brief.lower():
        issues.append("Horror cruft in brief — wrong niche")
        score -= 4
    passed = score >= 7.0 and not any("Horror" in i for i in issues)
    return ScriptQCResult(
        passed=passed,
        score=max(0.0, score),
        issues=issues,
        summary="Offline QC OK" if passed else "; ".join(issues),
    )


def score_script_brief(
    *,
    product: str,
    hook: str,
    brief: str,
    verdict_hint: str = "Pay, Skip, or Wait",
) -> ScriptQCResult:
    """Score brief before burning InVideo credits."""
    if not settings.script_qc_enabled:
        return ScriptQCResult(passed=True, score=10.0, issues=[], summary="QC disabled")

    if settings.has_gemini or settings.has_openai:
        try:
            return _llm_qc(product=product, hook=hook, brief=brief, verdict_hint=verdict_hint)
        except Exception as exc:
            offline = _offline_qc(
                product=product, hook=hook, brief=brief, verdict_hint=verdict_hint
            )
            offline.issues.append(f"LLM QC fallback: {exc}"[:80])
            return offline

    return _offline_qc(product=product, hook=hook, brief=brief, verdict_hint=verdict_hint)


def _llm_qc(*, product: str, hook: str, brief: str, verdict_hint: str) -> ScriptQCResult:
    prompt = f"""Score this YouTube Short product review brief (1-10).

Product: {product}
Hook: {hook}
Verdict hint: {verdict_hint}
Brief:
{brief[:2000]}

Rules: Pay/Skip/Wait niche, ~30s, clear verdict, no horror, hook under 15 words ideal.

Return JSON only:
{{"score": 8.5, "passed": true, "issues": ["..."], "summary": "one line"}}
"""
    if settings.has_gemini:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)
        resp = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )
        text = (resp.text or "").strip()
    else:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        text = resp.choices[0].message.content or "{}"

    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    data = json.loads(text.strip())
    score = float(data.get("score", 0))
    issues = [str(i) for i in data.get("issues") or []]
    passed = bool(data.get("passed", score >= 7.0))
    if score < settings.script_qc_min_score:
        passed = False
    return ScriptQCResult(
        passed=passed,
        score=score,
        issues=issues,
        summary=str(data.get("summary") or "")[:200],
    )
