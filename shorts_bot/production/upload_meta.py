"""YouTube upload metadata — Don't Blink horror Shorts SEO."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

HORROR_HASHTAGS = ("#Horror", "#HorrorShorts", "#Jumpscare", "#ScaryStories", "#Creepy")
HORROR_BACKEND_TAGS = [
    "horror shorts",
    "jumpscare",
    "scary stories",
    "creepy",
    "psychological horror",
    "faceless horror",
    "dont blink",
    "horror story",
    "short horror",
    "scary short",
]


@dataclass
class UploadPackage:
    title: str
    description: str
    tags: list[str]
    visibility: str
    checklist: list[str]


def build_upload_package(
    topic: str,
    hook: str,
    *,
    draft_id: int,
    research=None,
) -> UploadPackage:
    """Horror Short metadata: volume warning title, keyword-rich description, 5-8 backend tags."""
    from shorts_bot.config import settings
    from shorts_bot.production.niche import NICHE_NAME

    title = _title_from_research(topic, hook, research) if research else _safe_title(topic, hook)
    description = _description_from_research(topic, hook, research) if research else _safe_description(topic, hook)
    tags = _tags_from_research(topic, research) if research else list(HORROR_BACKEND_TAGS)
    visibility = settings.youtube_upload_visibility
    if visibility not in ("public", "unlisted", "private"):
        visibility = "unlisted"

    checklist = [
        f"Visibility: {visibility}",
        f"Niche: {NICHE_NAME}",
        "🔊 Volume warning in title + description (jumpscare at end)",
        "YPP: max 1 Short per 24h — upload_guard enforces",
        "Script is second-person horror micro-story — impossible hook in line 1",
        "Title front-loads hook keyword (first 40 chars); VO speaks hook in first 3s",
        "3-5 hashtags in description (first 3 show above title)",
        "5-8 backend tags in Studio — horror/jumpscare/topic-specific",
        "Disclose altered/synthetic media (API: containsSyntheticMedia)",
        "Captions in Jenny 05 safe zone — above Shorts title overlay",
        "After publish: sync analytics; read retention at 20s and final 3s",
    ]
    return UploadPackage(
        title=title,
        description=description,
        tags=tags,
        visibility=visibility,
        checklist=checklist,
    )


def _title_from_research(topic: str, hook: str, research) -> str:
    formula = (getattr(research, "title_formula", None) or "").strip()
    if formula:
        cleaned = _clean_title_formula(formula)
        if cleaned and len(cleaned) <= 100:
            return cleaned[:100]
    return _safe_title(topic, hook)


def _clean_title_formula(formula: str) -> str:
    """Strip hashtags and legacy prefixes; keep 🔊 volume warning."""
    t = re.sub(r"#\w+", "", formula).strip()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"^VOLUME WARNING:\s*", "", t, flags=re.I).strip()
    if t and not t.startswith("🔊"):
        t = f"🔊 {t}"
    return t.strip()


def _topic_hashtags(topic: str) -> list[str]:
    lower = topic.lower()
    tags: list[str] = []
    if "mirror" in lower or "reflection" in lower or "blink" in lower:
        tags.extend(["#MirrorHorror", "#Reflection"])
    if "security" in lower or "camera" in lower or "motion" in lower:
        tags.extend(["#SecurityCamera", "#FoundFootage"])
    if "text" in lower or "message" in lower or "delivered" in lower:
        tags.extend(["#WrongText", "#PhoneHorror"])
    if "knock" in lower or "closet" in lower or "door" in lower:
        tags.extend(["#KnockHorror", "#HomeAlone"])
    if "security" in lower or "camera" in lower or "motion" in lower:
        tags.extend(["#SecurityCamera", "#FoundFootage"])
    if "alone" in lower:
        tags.append("#HomeAlone")
    return tags[:3]


def _description_from_research(topic: str, hook: str, research) -> str:
    hook_line = hook.strip() if hook else topic.strip()
    topic_tags = _topic_hashtags(topic)
    base_hashtags = list(HORROR_HASHTAGS) + [t for t in topic_tags if t not in HORROR_HASHTAGS]
    hashtags = " ".join(base_hashtags[:5])

    extra = ""
    if getattr(research, "competitor_gap", None):
        gap = str(research.competitor_gap).strip()
        if gap and len(gap) < 200:
            extra = f"\n{gap}\n"

    return (
        f"🔊 VOLUME WARNING — jumpscare in the last 3 seconds. Headphones advised.\n\n"
        f"{hook_line}\n\n"
        f"PERIPHERAL — twisted horror micro-chapters (~30s). "
        f"One impossible detail → tension → scare at the edge. You're already in it.\n"
        f"{extra}\n"
        f"AI motion visuals · synthetic media disclosed\n\n"
        f"What should the next story be? One sentence in the comments.\n\n"
        f"{hashtags}"
    )


def _tags_from_research(topic: str, research) -> list[str]:
    base = list(HORROR_BACKEND_TAGS)
    seen = {t.lower() for t in base}
    for row in getattr(research, "keyword_insights", None) or []:
        kw = str(row.get("keyword", "")).strip().lower()
        if not kw or kw in seen or len(kw) > 40:
            continue
        if kw.startswith("#"):
            kw = kw.lstrip("#")
        base.append(kw)
        seen.add(kw)
        if len(base) >= 12:
            break
    lower = topic.lower()
    if "mirror" in lower and "mirror horror" not in seen:
        base.append("mirror horror")
    if "blink" in lower and "wrong reflection" not in seen:
        base.append("wrong reflection")
    if any(k in lower for k in ("security", "camera", "motion", "cctv")):
        for tag in ("security camera horror", "night vision", "home alone"):
            if tag not in seen:
                base.append(tag)
                seen.add(tag)
    if any(k in lower for k in ("text", "message", "delivered")):
        for tag in ("phone horror", "wrong text"):
            if tag not in seen:
                base.append(tag)
                seen.add(tag)
    return base[:12]


def _safe_title(topic: str, hook: str) -> str:
    """Front-load impossible hook; volume warning for horror."""
    slop_hooks = ("stop scrolling", "hey guys", "you won't believe")
    if hook and len(hook) < 85 and not any(s in hook.lower() for s in slop_hooks):
        clean = hook.strip()
        if not clean.upper().startswith("🔊"):
            return f"🔊 {clean}"[:100]
        return clean[:100]
    t = topic.strip()
    return f"🔊 {t[:80]} — you're already in it"[:100]


def _safe_description(topic: str, hook: str) -> str:
    hook_line = hook.strip() if hook else topic.strip()
    hashtags = " ".join(list(HORROR_HASHTAGS)[:5])
    return (
        f"🔊 VOLUME WARNING — jumpscare in the last 3 seconds. Headphones advised.\n\n"
        f"{hook_line}\n\n"
        f"PERIPHERAL — twisted horror micro-chapters (~30s). "
        f"You're already in it.\n\n"
        f"AI motion visuals · synthetic media disclosed\n\n"
        f"{hashtags}"
    )


def write_upload_files(pack_dir: Path, package: UploadPackage, *, draft_id: int) -> Path:
    meta = {
        "draft_id": draft_id,
        "title": package.title,
        "description": package.description,
        "tags": package.tags,
        "visibility": package.visibility,
        "checklist": package.checklist,
    }
    path = pack_dir / "upload_metadata.json"
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    md = pack_dir / "UPLOAD_READY.md"
    lines = [
        f"# Upload ready — draft {draft_id}",
        "",
        "## Video file",
        "`final_short.mp4`",
        "",
        "## Recommended settings (horror Shorts SEO)",
        f"- **Visibility:** {package.visibility}",
        f"- **Title:** {package.title}",
        "",
        "## Description",
        "```",
        package.description,
        "```",
        "",
        "## Backend tags (Studio)",
        ", ".join(package.tags),
        "",
        "## Checklist",
    ]
    lines.extend(f"- {c}" for c in package.checklist)
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
