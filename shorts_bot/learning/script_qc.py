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
_SHOP_MARKERS = re.compile(r"\b(problem|demo|shop cta|orange cart|shopping bag|fix it fast)\b", re.I)


def _is_shop_brief(brief: str) -> bool:
    return bool(_SHOP_MARKERS.search(brief[:800]))


_BRIEF_BOILERPLATE = re.compile(
    r"(NO Pay / Skip / Wait|NO AI Twin|DO NOT:)[\s\S]*?(?=PRODUCT:|LESSON TOPIC:|$)",
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
    if product.lower() not in hook.lower() and product.lower() not in brief.lower()[:400]:
        parts = [w for w in re.findall(r"[a-z0-9]+", product.lower()) if len(w) > 3]
        if parts and not any(p in hook.lower() or p in brief.lower()[:400] for p in parts):
            issues.append("Product name missing from hook/opening")
            score -= 2
    if _has_verdict_stamp(_brief_for_qc(brief)) or _has_verdict_stamp(verdict_hint):
        issues.append("Pay/Skip/Wait language — use Shop problem/demo format")
        score -= 3
    if _is_shop_brief(brief):
        if not _SHOP_MARKERS.search(brief):
            issues.append("Missing Shop demo/CTA framing")
            score -= 2
    elif not _STRENGTH_WEAKNESS.search(brief):
        issues.append("Missing problem/demo framing")
        score -= 3
    if _is_shop_brief(brief):
        body = _brief_for_qc(brief).lower()
        if "horror" in body or "jumpscare" in body:
            issues.append("Horror cruft in brief — wrong niche")
            score -= 4
        if re.search(r"\bms\. byte\b", body) and "no ms. byte" not in body:
            issues.append("Ms. Byte cruft — retired format")
            score -= 4
    elif not _JENNY_MARKERS.search(brief):
        issues.append("Missing conversational movement (but/so or you decide)")
        score -= 1
    if _TTS_X_AS_WORD.search(hook):
        issues.append('TTS risk: say "Twitter" not "X" as a spoken word')
        score -= 2
    if "class is in session" in hook.lower()[:40]:
        issues.append("Hook starts with classroom warm-up — show problem first")
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
    prompt = f"""Score this TikTok Shop gadget Short brief (1-10).

Product: {product}
Hook: {hook}
Brief:
{brief[:2000]}

Rules: Fix It Fast format — ONE physical product, problem visible in hook,
hands/product demo, satisfying fix, Shop CTA (orange cart / shopping bag),
15-30s, 9:16 vertical, NO AI tool reviews, NO Ms. Byte, NO Pay/Skip/Wait,
NO listicles, NO horror, hook under 18 words ideal.
Shop note: {verdict_hint}

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
