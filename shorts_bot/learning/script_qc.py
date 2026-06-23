"""Pre-InVideo script QC — Gemini when available, heuristics offline."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from shorts_bot.config import settings
from shorts_bot.production.hooks import score_hook

_VERDICT_WORDS = re.compile(r"\b(Pay|Skip|Wait)\b", re.I)
_STRENGTH_WEAKNESS = re.compile(r"\b(strength|weakness|pro|con|tradeoff)\b", re.I)
_JENNY_MARKERS = re.compile(r"\b(but|so|you decide)\b", re.I)
_TTS_X_AS_WORD = re.compile(
    r"\b(live X\b|trends on X\b|on X —|If X isn't|Comment X person|X person or not|X posts\b|about X\b)",
    re.I,
)
# Ms. Byte brief template includes negation examples — strip before verdict/TTS scans.
_BRIEF_BOILERPLATE = re.compile(
    r"(NO Pay / Skip / Wait|TTS LEXICON|NEVER say the letter \"X\"|NOT \"live X posts\")[\s\S]*?(?=LESSON TOPIC:|$)",
    re.I,
)


def _brief_for_qc(brief: str) -> str:
    return _BRIEF_BOILERPLATE.sub("", brief)


def _has_verdict_stamp(text: str) -> bool:
    kept: list[str] = []
    for line in text.splitlines():
        lower = line.lower()
        if any(
            p in lower
            for p in (
                "no pay",
                "not pay",
                "do not",
                "don't",
                "never",
                "no ai twin",
                "not pay/skip",
            )
        ):
            continue
        kept.append(line)
    return bool(_VERDICT_WORDS.search("\n".join(kept)))


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
    if product.lower() not in hook.lower() and product.lower() not in brief.lower()[:300]:
        issues.append("Product name missing from hook/opening")
        score -= 2
    if _has_verdict_stamp(_brief_for_qc(brief)) or _has_verdict_stamp(verdict_hint):
        issues.append("Pay/Skip/Wait language — Ms. Byte uses strength/weakness format")
        score -= 3
    if not _STRENGTH_WEAKNESS.search(brief):
        issues.append("Missing strength/weakness framing")
        score -= 3
    if not _JENNY_MARKERS.search(brief):
        issues.append("Missing Jenny but/so or 'you decide' movement")
        score -= 1
    if _TTS_X_AS_WORD.search(hook):
        issues.append('TTS risk: say "Twitter" not "X" as a spoken word')
        score -= 2
    if "horror" in brief.lower() or "jumpscare" in brief.lower():
        issues.append("Horror cruft in brief — wrong niche")
        score -= 4
    if "class is in session" in hook.lower()[:40]:
        issues.append("Hook starts with classroom warm-up — curiosity should come first (Jenny 02)")
        score -= 2
    hook_score, hook_issues = score_hook(hook)
    if hook_score < 7.0:
        issues.extend(hook_issues[:3])
        score -= max(1.0, (7.0 - hook_score))
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
    verdict_hint: str = "",
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
Brief:
{brief[:2000]}

Rules: Ms. Byte format — ONE strength + ONE weakness, Jenny 8-beat structure,
curiosity hook BEFORE host intro (price shock, contrarian, or "most shouldn't pay"),
NO generic "is X worth it" or "I tested if", CTA before payoff, ~30s, NO Pay/Skip/Wait stamps,
NO horror, hook under 15 words ideal, say "Twitter" not "X" as spoken word in VO.
Verdict hint (legacy, penalize if Pay/Skip/Wait): {verdict_hint}

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
