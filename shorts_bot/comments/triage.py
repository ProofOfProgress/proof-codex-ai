"""Classify comments: auto-reply vs leave for channel owner."""

from __future__ import annotations

import re
from dataclasses import dataclass

SERIOUS_PATTERNS = [
    re.compile(p, re.I)
    for p in (
        r"\b(suicid|kill myself|killing myself|self[- ]?harm|hurt myself|end my life|end it all)\b",
        r"\b(want to die|don't want to live|do not want to live|no reason to live)\b",
        r"\b(988|crisis line|crisis hotline|emergency help)\b",
        r"\b(abuse|abused|assault|raped|rape|domestic violence|molest)\b",
        r"\b(trauma|ptsd|panic attack|mental breakdown|hospitalized|psych ward)\b",
        r"\b(grief|passed away|died|funeral|miscarriage|stillborn)\b",
        r"\b(diagnos(e|ed|is)|medication|prescri|psychiat|therapist|counselor)\b",
        r"\b(overdose|od\b|cutting\b|cut myself)\b",
        r"\b(lawsuit|sue you|legal action|custody battle)\b",
        r"\b(stalk|harass|threaten|death threat)\b",
        r"\b(hopeless|worthless|can't go on|cannot go on)\b",
        r"\b(sexual abuse|child abuse)\b",
    )
]

MEDICAL_ADVICE = re.compile(
    r"\b(should i take|is it safe to|medical advice|what medicine|dosage|symptom)\b",
    re.I,
)

SPAM_PATTERNS = [
    re.compile(p, re.I)
    for p in (
        r"https?://",
        r"\b(subscribe to my|check out my channel|dm me for|crypto|forex|onlyfans)\b",
        r"\b(free followers|giveaway click)\b",
    )
]

TOPIC_REQUEST = re.compile(
    r"\b(minute before|cover|do (a|one on)|topic|next short|please make|can you do)\b",
    re.I,
)


@dataclass
class TriageResult:
    decision: str  # auto | human | spam | skip
    reason: str


def triage_comment(text: str, *, author: str = "") -> TriageResult:
    """Route comment: auto-reply, human queue, spam ignore, or skip empty."""
    body = (text or "").strip()
    if not body or len(body) < 2:
        return TriageResult("skip", "empty")

    for pat in SPAM_PATTERNS:
        if pat.search(body):
            return TriageResult("spam", "spam/link pattern")

    for pat in SERIOUS_PATTERNS:
        if pat.search(body):
            return TriageResult("human", f"serious topic: {pat.pattern[:40]}")

    if MEDICAL_ADVICE.search(body):
        return TriageResult("human", "medical advice request")

    # Long emotional vents — you should read these
    if len(body) > 420:
        return TriageResult("human", "long personal vent")

    # Multiple question marks + distress cues
    if body.count("?") >= 3 and re.search(r"\b(why me|help me|please help|so alone)\b", body, re.I):
        return TriageResult("human", "distress + multiple asks")

    # Channel owner name confusion / collaboration — human
    if re.search(r"\b(collab|sponsor|business|invoice|payment)\b", body, re.I):
        return TriageResult("human", "business/collab")

    return TriageResult("auto", "routine engagement")
