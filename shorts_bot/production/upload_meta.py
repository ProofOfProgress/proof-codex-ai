"""YouTube / TikTok upload metadata — Fix It Fast TikTok Shop gadget Shorts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

HORROR_HASHTAGS = ("#Horror", "#HorrorShorts", "#ScaryStories", "#Creepy")
SHOP_HASHTAGS = ("#tiktokshop", "#gadget", "#homehack", "#fixitfast", "#amazonfinds")
SHOP_BACKEND_TAGS = [
    "tiktok shop",
    "gadget",
    "home hack",
    "kitchen hack",
    "car hack",
    "problem solved",
    "fix it fast",
]
AI_REVIEW_HASHTAGS = SHOP_HASHTAGS  # legacy import alias
AI_BACKEND_TAGS = SHOP_BACKEND_TAGS
HORROR_HASHTAGS_JUMPSCARE = ("#Horror", "#HorrorShorts", "#Jumpscare", "#ScaryStories", "#Creepy")
HORROR_BACKEND_TAGS = [
    "horror shorts",
    "jumpscare",
    "scary stories",
    "creepy",
    "psychological horror",
    "analog horror",
    "found footage",
    "faceless horror",
    "peripheral horror",
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


def _volume_warning_for_draft(draft_id: int) -> str:
    from shorts_bot.production.description_copy import volume_warning_for_plan
    from shorts_bot.production.jumpscare_timing import load_plan_for_draft

    plan = load_plan_for_draft(draft_id, 8)
    return volume_warning_for_plan(
        has_jumpscare=plan.has_jumpscare,
        raw_warning=plan.volume_warning,
    )


def build_upload_package(
    topic: str,
    hook: str,
    *,
    draft_id: int,
    research=None,
) -> UploadPackage:
    """Upload metadata for the active Rapid Tool Review niche, with horror archive fallback."""
    from shorts_bot.config import settings
    from shorts_bot.production.niche import NICHE_NAME

    title = (
        _title_from_research(topic, hook, research)
        if research
        else _safe_title(topic, hook, draft_id=draft_id)
    )
    description = _description_from_research(
        topic, hook, research, draft_id=draft_id
    ) if research else _safe_description(topic, hook, draft_id=draft_id)
    tags = _tags_from_research(topic, research) if research else (
        _ai_review_tags(topic) if _is_ai_review_topic(topic) else list(HORROR_BACKEND_TAGS)
    )
    visibility = settings.youtube_upload_visibility
    if visibility not in ("public", "unlisted", "private"):
        visibility = "unlisted"

    checklist = [
        f"Visibility: {visibility}",
        f"Niche: {NICHE_NAME}",
        "No horror volume warning on AI product reviews",
        "YPP: max 1 Short per 24h — upload_guard enforces",
        "Script gives one clear AI-tool takeaway in ~30 seconds",
        "Title front-loads product + verdict; VO speaks hook in first 3s",
        "3-5 hashtags in description (first 3 show above title)",
        "5-8 backend tags in Studio — AI/tool/product-specific",
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
    """Strip hashtags and legacy prefixes; keep 🔊 volume warning when appropriate."""
    from shorts_bot.compliance.ypp_bans import RESEARCH_TITLE_BLOCK_RE

    t = re.sub(r"#\w+", "", formula).strip()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"^VOLUME WARNING:\s*", "", t, flags=re.I).strip()
    for pat in RESEARCH_TITLE_BLOCK_RE:
        if pat.search(t):
            return ""
    if len(t) > 12 and sum(1 for c in t if c.isupper()) > len(t) * 0.55:
        return ""
    return t.strip()


def _phones_in_upload_meta() -> bool:
    from shorts_bot.config import settings

    return bool(settings.screen_text_phone_enabled)


def _topic_hashtags(topic: str) -> list[str]:
    from shorts_bot.production.screen_text_spec import is_cctv_topic

    lower = topic.lower()
    tags: list[str] = []
    if "mirror" in lower or "reflection" in lower or "blink" in lower:
        tags.extend(["#MirrorHorror", "#Reflection"])
    if is_cctv_topic(topic) or any(k in lower for k in ("security", "camera", "motion", "cctv")):
        tags.extend(["#AnalogHorror", "#SecurityCamera", "#FoundFootage"])
    if "text" in lower or "message" in lower or "delivered" in lower:
        if _phones_in_upload_meta():
            tags.extend(["#WrongText", "#PhoneHorror"])
        else:
            tags.append("#AnalogHorror")
    if "knock" in lower or "closet" in lower or "door" in lower:
        tags.extend(["#KnockHorror", "#HomeAlone"])
    if "alone" in lower:
        tags.append("#HomeAlone")
    # dedupe while preserving order
    seen: set[str] = set()
    ordered: list[str] = []
    for tag in tags:
        if tag not in seen:
            ordered.append(tag)
            seen.add(tag)
    return ordered[:3]


def _normalize_horror_hook(hook: str, topic: str) -> str:
    """Prefer second-person hook line for descriptions."""
    line = (hook or topic).strip()
    line = re.sub(r"\bMy\b", "Your", line)
    line = re.sub(r"\bmy\b", "your", line)
    line = re.sub(r"\bI live alone\b", "you live alone", line, flags=re.I)
    line = re.sub(r"\bI\b", "you", line)
    return line.strip()


def _description_from_research(topic: str, hook: str, research, *, draft_id: int = 0) -> str:
    from shorts_bot.production.description_copy import story_tease_line
    from shorts_bot.production.jumpscare_timing import load_plan_for_draft

    hook_line = _normalize_horror_hook(hook, topic)
    topic_tags = _topic_hashtags(topic)
    vol = _volume_warning_for_draft(draft_id) if draft_id else ""
    has_js = load_plan_for_draft(draft_id, 8).has_jumpscare if draft_id else True
    tag_base = HORROR_HASHTAGS_JUMPSCARE if has_js else HORROR_HASHTAGS
    base_hashtags = list(tag_base) + [t for t in topic_tags if t not in tag_base]
    hashtags = " ".join(base_hashtags[:5])
    scare_line = story_tease_line(has_jumpscare=has_js and bool(vol.strip()))
    lines = [vol, hook_line] if vol.strip() else [hook_line]
    lines.extend(
        [
            f"Peripheral — scary horror Shorts (~30s). {scare_line}\n\ndon't blink.",
            "AI motion visuals · synthetic media disclosed",
            "What should the next story be? One sentence in the comments.",
            hashtags,
        ]
    )
    from shorts_bot.production.description_copy import sanitize_description_text

    return sanitize_description_text("\n\n".join(lines))


def _topic_backend_tags(topic: str) -> list[str]:
    """Topic-specific Studio tags — merged before generic horror defaults."""
    lower = topic.lower()
    tags: list[str] = []
    if "mirror" in lower:
        tags.append("mirror horror")
    if "blink" in lower:
        tags.append("wrong reflection")
    if any(k in lower for k in ("security", "camera", "motion", "cctv")):
        tags.extend(
            [
                "security camera horror",
                "surveillance horror",
                "night vision",
                "home alone",
            ]
        )
    if any(k in lower for k in ("text", "message", "delivered")):
        if _phones_in_upload_meta():
            tags.extend(["phone horror", "wrong text"])
        else:
            tags.extend(["analog horror", "wrong text"])
    return tags


def _tags_from_research(topic: str, research) -> list[str]:
    base: list[str] = []
    seen: set[str] = set()
    for row in getattr(research, "keyword_insights", None) or []:
        kw = str(row.get("keyword", "")).strip().lower()
        if not kw or kw in seen or len(kw) > 40:
            continue
        if kw.startswith("#"):
            kw = kw.lstrip("#")
        base.append(kw)
        seen.add(kw)
    for tag in _topic_backend_tags(topic) + list(HORROR_BACKEND_TAGS):
        if len(base) >= 12:
            break
        key = tag.lower()
        if key in seen or len(tag) > 40:
            continue
        base.append(tag)
        seen.add(key)
    return base[:12]


def _is_horror_topic(topic: str) -> bool:
    lower = topic.lower()
    markers = (
        "horror", "jumpscare", "scary", "creepy", "peripheral", "don't blink",
        "analog horror", "security cam", "3:12 am", "faceless horror",
    )
    return any(m in lower for m in markers)


def _is_ai_review_topic(topic: str) -> bool:
    """Fix It Fast Shop default — horror archive topics use legacy meta."""
    return not _is_horror_topic(topic)


def _ai_review_tags(topic: str) -> list[str]:
    tags = list(AI_BACKEND_TAGS)
    lower = topic.lower()
    if "claude" in lower:
        tags.insert(0, "claude code")
    if "chatgpt" in lower:
        tags.insert(0, "chatgpt")
    return tags[:8]


def _safe_title(topic: str, hook: str, *, draft_id: int = 0) -> str:
    """Front-load hook line; skip horror volume prefix on AI reviews."""
    vol_prefix = ""
    if draft_id and not _is_ai_review_topic(topic) and _volume_warning_for_draft(draft_id).strip():
        vol_prefix = "🔊 "
    slop_hooks = ("stop scrolling", "hey guys", "you won't believe")
    if hook and len(hook) < 85 and not any(s in hook.lower() for s in slop_hooks):
        clean = hook.strip()
        if clean.upper().startswith("🔊"):
            clean = clean.lstrip("🔊").strip()
        return f"{vol_prefix}{clean}"[:100]
    t = topic.strip()
    return f"{vol_prefix}{t[:95]}"[:100]


def _safe_description(topic: str, hook: str, *, draft_id: int = 0) -> str:
    hook_line = hook.strip() or topic.strip()
    if _is_ai_review_topic(topic):
        hashtags = " ".join(AI_REVIEW_HASHTAGS)
        lines = [
            hook_line,
            "Fix It Fast — TikTok Shop gadget demo (~20s). Problem → fix → cart.",
            "Synthetic/stock visuals disclosed where applicable.",
            hashtags,
        ]
        from shorts_bot.production.description_copy import sanitize_description_text

        return sanitize_description_text("\n\n".join(lines))

    hook_line = _normalize_horror_hook(hook, topic)
    from shorts_bot.production.jumpscare_timing import load_plan_for_draft

    vol = _volume_warning_for_draft(draft_id) if draft_id else ""
    has_js = load_plan_for_draft(draft_id, 8).has_jumpscare if draft_id else True
    tag_base = HORROR_HASHTAGS_JUMPSCARE if has_js else HORROR_HASHTAGS
    hashtags = " ".join(list(tag_base)[:5])
    from shorts_bot.production.description_copy import story_tease_line, sanitize_description_text
    tease = story_tease_line(has_jumpscare=has_js and bool(vol.strip()))
    lines = [vol, hook_line] if vol.strip() else [hook_line]
    lines.extend(
        [
            sanitize_description_text(
                f"Peripheral — scary horror Shorts (~30s). "
                f"{tease} Watch the whole thing.\n\ndon't blink."
            ),
            "AI motion visuals · synthetic media disclosed",
            hashtags,
        ]
    )
    from shorts_bot.production.description_copy import sanitize_description_text

    return sanitize_description_text("\n\n".join(lines))


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
        "## Recommended settings (Rapid Tool Review SEO)",
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
