"""B2B outreach — human-sounding DMs and emails for AI tool Shorts service."""

from __future__ import annotations

import re
from dataclasses import dataclass

from shorts_bot.production.scene_plan import ai_likelihood_score

# Obvious AI / sales-bro phrases — reject or strip in outreach.
BANNED_PHRASES: tuple[str, ...] = (
    "i hope this email finds you well",
    "i hope this message finds you well",
    "i'm reaching out because",
    "i am reaching out because",
    "i'd love to pick your brain",
    "i would love to pick your brain",
    "excited to connect",
    "synergy",
    "leverage",
    "innovative solution",
    "game-changer",
    "game changer",
    "delve",
    "tapestry",
    "furthermore",
    "moreover",
    "in conclusion",
    "at your earliest convenience",
    "circle back",
    "touch base",
    "value proposition",
    "best-in-class",
    "cutting-edge",
    "revolutionary",
    "i wanted to introduce",
    "hope you're doing well",
    "trust this email finds you",
)

MAX_DM_WORDS = 85
MAX_EMAIL_WORDS = 120


@dataclass
class OutreachDraft:
    channel: str  # dm | email
    body: str
    subject: str | None
    ai_score: int
    issues: list[str]
    passed: bool


def _scrub_slop(text: str) -> str:
    t = text.strip()
    t = re.sub(r"\s—\s", ", ", t)
    t = t.replace("—", ", ")
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    swaps = {
        "Do not": "Don't",
        "do not": "don't",
        "It is": "It's",
        "it is": "it's",
        "You are": "You're",
        "you are": "you're",
        "I am": "I'm",
        "We are": "We're",
        "cannot": "can't",
        "will not": "won't",
    }
    for a, b in swaps.items():
        t = t.replace(a, b)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _find_banned(text: str) -> list[str]:
    lower = text.lower()
    return [p for p in BANNED_PHRASES if p in lower]


def _word_count(text: str) -> int:
    return len(text.split())


def score_outreach(text: str, *, channel: str = "dm") -> tuple[int, list[str]]:
    issues: list[str] = []
    score = ai_likelihood_score(text)
    issues.extend(f"banned phrase: {p}" for p in _find_banned(text))
    if issues:
        score = min(100, score + len(issues) * 8)
    limit = MAX_DM_WORDS if channel == "dm" else MAX_EMAIL_WORDS
    wc = _word_count(text)
    if wc > limit:
        issues.append(f"too long ({wc} words, max {limit})")
        score += 10
    if wc < 25 and channel == "email":
        issues.append("email too thin — add one specific detail")
        score += 5
    if not re.search(r"\b(i'm|i've|i run|we make|we're|my|our)\b", text, re.I):
        issues.append("needs first-person voice (I/my/we)")
        score += 15
    if "?" not in text and channel == "dm":
        issues.append("DM should end with one easy question")
        score += 5
    return score, issues


def _offline_dm(*, company: str, product: str, detail: str, sample_url: str, sender: str) -> str:
    detail_bit = f" {detail.strip().rstrip('.')}." if detail.strip() else ""
    return (
        f"Hey — saw {product}{detail_bit} "
        f"I run Rapid Tool Review (30s honest AI tool Shorts, synthetic host Ms. Byte). "
        f"Made a sample breakdown style video — happy to do a pilot for {company} if useful. "
        f"Worth a look? {sample_url} — {sender.split()[0] if sender else 'Kim'}"
    )


def _offline_email_subject(product: str) -> str:
    return f"30s review Short for {product}? (sample inside)"


def _offline_email(*, company: str, product: str, detail: str, sample_url: str, sender: str) -> str:
    detail_bit = detail.strip().rstrip(".") or "your launch"
    first = sender.split()[0] if sender else "Kim"
    return (
        f"Hi,\n\n"
        f"Saw {detail_bit} for {product} — caught my eye.\n\n"
        f"I run Rapid Tool Review: ~30 second tool breakdowns (one strength, one weakness). "
        f"We use a synthetic host (Ms. Byte) on purpose — it's clearly AI, but the reviews are real.\n\n"
        f"Sample: {sample_url}\n\n"
        f"If you'd want a pilot Short for {company}, reply here and I'll send pricing. "
        f"No pressure either way.\n\n"
        f"{first}"
    )


def draft_outreach(
    *,
    company: str,
    product: str,
    detail: str = "",
    sample_url: str = "https://youtube.com/shorts/FRGbCIH5R1k",
    sender_name: str = "Kim",
    channel: str = "dm",
    max_attempts: int = 3,
) -> OutreachDraft:
    """Draft a human-sounding B2B message. Retries if AI score too high."""
    channel = channel.lower().strip()
    if channel not in ("dm", "email"):
        raise ValueError("channel must be dm or email")

    from shorts_bot.config import settings
    from shorts_bot.llm.provider import get_llm_backend

    sender = sender_name or "Kim"
    backend = get_llm_backend()

    prompt = f"""Write a B2B cold outreach message as {sender}, a real founder (NOT a bot persona).

Service: Rapid Tool Review — 30s YouTube Shorts reviewing AI tools honestly. Synthetic host "Ms. Byte" on video (disclosed). Pilot Shorts for startups.

Prospect:
- Company: {company}
- Product: {product}
- Specific detail you MUST mention (proves you looked): {detail or "recent launch"}

Sample video URL to include: {sample_url}

Channel: {channel.upper()}
{"Max 85 words. One short paragraph. Casual Twitter DM tone. Lowercase ok for hey." if channel == "dm" else "Max 120 words. Short email. Subject line required."}

HUMAN RULES (critical):
- First person (I/my/we). Sound like one person typing on their phone.
- Mention ONE specific fact about their product/launch — not generic praise.
- End with ONE easy yes/no question.
- Contractions (don't, it's, we're). Mix short and medium sentences.
- NO: "I hope this finds you well", "reaching out", "synergy", "leverage", "excited to connect", em dashes, bullet lists, numbered lists.
- NO corporate signature blocks. Sign first name only for email.
- Do NOT say you are an AI. Do NOT say the message was AI-generated. Write like a human founder.

Return JSON only:
{{"subject": "..." or null for dm, "body": "..."}}"""

    best_body = ""
    best_subject: str | None = None
    best_score = 100
    best_issues: list[str] = []

    if backend is None:
        body = _offline_dm(
            company=company,
            product=product,
            detail=detail,
            sample_url=sample_url,
            sender=sender,
        ) if channel == "dm" else _offline_email(
            company=company,
            product=product,
            detail=detail,
            sample_url=sample_url,
            sender=sender,
        )
        subject = None if channel == "dm" else _offline_email_subject(product)
        score, issues = score_outreach(body, channel=channel)
        return OutreachDraft(
            channel=channel,
            body=body,
            subject=subject,
            ai_score=score,
            issues=issues,
            passed=score <= 25 and not _find_banned(body),
        )

    for _ in range(max_attempts):
        try:
            resp = backend.client.chat.completions.create(
                model=backend.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You write cold outreach that sounds human-written. JSON only.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.9,
            )
            import json

            payload = json.loads(resp.choices[0].message.content or "{}")
            body = _scrub_slop(str(payload.get("body") or ""))
            subject = payload.get("subject")
            subject = _scrub_slop(str(subject)) if subject else None
        except Exception:
            body = _offline_dm(
                company=company,
                product=product,
                detail=detail,
                sample_url=sample_url,
                sender=sender,
            ) if channel == "dm" else _offline_email(
                company=company,
                product=product,
                detail=detail,
                sample_url=sample_url,
                sender=sender,
            )
            subject = None if channel == "dm" else _offline_email_subject(product)

        if not body:
            continue
        score, issues = score_outreach(body, channel=channel)
        if score < best_score:
            best_score = score
            best_body = body
            best_subject = subject if channel == "email" else None
            best_issues = issues
        if score <= 20 and not _find_banned(body):
            break

    if channel == "email" and not best_subject:
        best_subject = _offline_email_subject(product)

    passed = best_score <= 25 and not _find_banned(best_body) and not any(
        "first-person" in i for i in best_issues
    )
    return OutreachDraft(
        channel=channel,
        body=best_body,
        subject=best_subject,
        ai_score=best_score,
        issues=best_issues,
        passed=passed,
    )
