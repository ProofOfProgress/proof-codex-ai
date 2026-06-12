"""Hard YPP / inauthentic-content bans — Jul 2025 policy enforcement.

YouTube policy: original, authentic content; not mass-produced template output.
These checks apply at channel level — one bad pattern can affect whole channel.
"""

from __future__ import annotations

import re

from shorts_bot.production.metal_aesthetic import script_animal_harm_issues

# QA iteration uploads (same draft, build v1/v2/…) — classic spam-farm signal
QA_ITERATION_TITLE_RE = re.compile(
    r"\(build\s+v\d+|\(v\d+\s+(sync|fixed|regen|scrub|ui|phone|screen|latest)\)",
    re.I,
)

# Engagement-bait metadata (advertiser-friendly + inauthentic signals)
METADATA_BAIT_PHRASES = (
    "watch twice if you missed",
    "watch till the end",
    "watch until the end",
    "you won't believe",
    "gone wrong",
    "instant regret",
    "number one will shock",
    "smash that like",
    "subscribe for more",
)

# Hashtags in titles — tag-stuffing / misleading discovery
HASHTAG_IN_TITLE_RE = re.compile(r"#\w+")

# Research title formulas that must never reach Studio
RESEARCH_TITLE_BLOCK_RE = [
    re.compile(r"DON'T\s+BLINK\s*#", re.I),
    re.compile(r"#shorts\s*#horror", re.I),
    re.compile(r"\[Pillar\s+Theme\]", re.I),
    re.compile(r"\[Impossible\s+Detail\]", re.I),
]

# Off-niche research cache markers (wrong vertical for Don't Blink)
OFF_NICHE_RESEARCH_MARKERS = (
    "better-mornings",
    "better mornings",
    "self-help",
    "productivity tips",
    "sleep tips",
    "morning routine",
)


def is_qa_iteration_title(title: str) -> bool:
    return bool(QA_ITERATION_TITLE_RE.search(title or ""))


def metadata_bait_issues(*parts: str) -> list[str]:
    issues: list[str] = []
    blob = " ".join(p for p in parts if p).lower()
    for phrase in METADATA_BAIT_PHRASES:
        if phrase in blob:
            issues.append(f"engagement-bait metadata: {phrase!r}")
    return issues


def title_compliance_issues(title: str) -> list[str]:
    issues: list[str] = []
    t = (title or "").strip()
    if not t:
        issues.append("empty title")
        return issues
    if is_qa_iteration_title(t):
        issues.append(
            "QA iteration title (build vN / vN sync) — batch same-topic uploads are "
            "inauthentic-content policy violations; use private local preview only"
        )
    if HASHTAG_IN_TITLE_RE.search(t):
        issues.append("hashtags in title — tag-stuffing / misleading metadata")
    if len(t) > 12 and sum(1 for c in t if c.isupper()) > len(t) * 0.6:
        issues.append("ALL CAPS shock title — engagement bait")
    for pat in RESEARCH_TITLE_BLOCK_RE:
        if pat.search(t):
            issues.append(f"blocked research title template: {pat.pattern[:40]}")
    return issues


def research_topic_is_off_niche(topic_or_path: str) -> bool:
    lower = (topic_or_path or "").lower()
    return any(m in lower for m in OFF_NICHE_RESEARCH_MARKERS)


def script_content_compliance_issues(*parts: str) -> list[str]:
    """Block explicit animal-harm language that risks age restriction / strikes."""
    return script_animal_harm_issues(*parts)


def batch_upload_forbidden_message() -> str:
    return (
        "Batch upload of multiple builds for one draft is BANNED under YPP_SAFE_MODE "
        "(YouTube inauthentic / mass-produced content policy). "
        "Preview builds locally or set YPP_ALLOW_BATCH_SERIES_UPLOAD=true only for "
        "non-monetized test channels with explicit owner approval."
    )
