"""Deep research — web, Google Trends, vidIQ, YouTube competitors, Jenny synthesis."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.production.framing import framing_notes_for_prompt
from shorts_bot.production.niche import NICHE_POSITIONING, quality_lessons


@dataclass
class ProductionResearch:
    topic: str
    niche: str
    viewer_moment: str
    emotional_stakes: str
    hook_angles: list[str]
    script_beats: list[str]
    visual_framing: str
    competitor_gap: str
    title_formula: str
    jenny_citations: list[str] = field(default_factory=list)
    quality_notes: str = ""
    researched_at: str = ""
    # Deep research extensions
    web_sources: list[dict] = field(default_factory=list)
    competitor_titles: list[str] = field(default_factory=list)
    keyword_insights: list[dict] = field(default_factory=list)
    recommended_path: str = ""
    search_queries: list[str] = field(default_factory=list)
    research_sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "niche": self.niche,
            "viewer_moment": self.viewer_moment,
            "emotional_stakes": self.emotional_stakes,
            "hook_angles": self.hook_angles,
            "script_beats": self.script_beats,
            "visual_framing": self.visual_framing,
            "competitor_gap": self.competitor_gap,
            "title_formula": self.title_formula,
            "jenny_citations": self.jenny_citations,
            "quality_notes": self.quality_notes,
            "researched_at": self.researched_at,
            "web_sources": self.web_sources,
            "competitor_titles": self.competitor_titles,
            "keyword_insights": self.keyword_insights,
            "recommended_path": self.recommended_path,
            "search_queries": self.search_queries,
            "research_sources": self.research_sources,
        }

    def draft_context(self) -> str:
        hooks = "\n".join(f"- {h}" for h in self.hook_angles[:4])
        beats = "\n".join(f"- {b}" for b in self.script_beats[:6])
        cites = ", ".join(self.jenny_citations) or "Jenny 02 hook, 05 mute-safe framing, 06 retention"
        competitors = ""
        if self.competitor_titles:
            competitors = "\nCompetitor Short titles:\n" + "\n".join(
                f"- {t}" for t in self.competitor_titles[:6]
            )
        keywords = ""
        if self.keyword_insights:
            keywords = "\nKeyword / SEO signals:\n" + "\n".join(
                f"- {k.get('keyword', '')} (vol={k.get('volume', '?')}, comp={k.get('competition', '?')})"
                for k in self.keyword_insights[:8]
            )
        path = ""
        if self.recommended_path:
            path = f"\nFastest path to run:\n{self.recommended_path}\n"
        trends = ""
        trend_rows = [k for k in self.keyword_insights if str(k.get("score", "")).startswith("trends_")]
        if trend_rows:
            trends = "\nGoogle Trends (YouTube search):\n" + "\n".join(
                f"- {k.get('keyword', '')} ({k.get('score', 'trends')})"
                for k in trend_rows[:8]
            )
        return f"""DEEP RESEARCH (web + Google Trends + vidIQ + Jenny — use this, do not genericize):
Niche: {self.niche}
Viewer moment: {self.viewer_moment}
Stakes: {self.emotional_stakes}
Competitor gap: {self.competitor_gap}
Title formula: {self.title_formula}
{competitors}{trends}{keywords}{path}
Hook angles (pick strongest):
{hooks}

Script beats (hook → momentum → payoff):
{beats}

Visual framing: {self.visual_framing}
Jenny course refs: {cites}
Quality bar: {self.quality_notes}
Sources used: {", ".join(self.research_sources) or "llm+course"}
"""

    def summary_for_chat(self, *, max_chars: int = 2800) -> str:
        return self.draft_context()[:max_chars]


_RESEARCH_PROMPT = """You are a YouTube Shorts production researcher for faceless channel Soft Continuity.

Your job: DEEP RESEARCH — not generic advice. Use the live web data, competitor titles, and keyword signals below.
Cross-check with Jenny Hoyos course rules. Recommend the smoothest, fastest pipeline path to publish.

NICHE POSITIONING:
{niche_block}

QUALITY LESSONS (channel performance):
{quality_lessons}

LIVE WEB RESEARCH:
{web_context}

YOUTUBE COMPETITOR SHORTS (real titles):
{competitor_context}

KEYWORD / SEO SIGNALS (YouTube suggest + Google Trends):
{keyword_context}

GOOGLE TRENDS (YouTube search interest, related + rising queries):
{trends_context}

JENNY HOYOS COURSE — cite file numbers in jenny_citations:
- 02: hook linked to idea, start ASAP
- 05: mute-safe visuals, rule of thirds, safe zones (captions above Shorts UI)
- 06: cause-effect script, payoff at end
- 07: relatability filter

Topic to research: {topic}

Return JSON only:
{{
  "viewer_moment": "one specific second the viewer is in",
  "emotional_stakes": "what they fear if they do nothing",
  "hook_angles": ["3 curiosity hooks, first person, under 12 words each"],
  "script_beats": ["5-7 beats: hook, struggle, turn, one protocol, slip, try tonight, payoff"],
  "visual_framing": "how to frame AI stills — subject upper 60%, bottom empty for captions",
  "competitor_gap": "what real Shorts miss — cite patterns from competitor titles/web data",
  "title_formula": "SEO-aware title using keyword signals, not rage-bait",
  "jenny_citations": ["Jenny 05", "Jenny 06"],
  "quality_notes": "how to beat generic slop on this topic",
  "recommended_path": "smoothest fastest link to run: daily CLI, research cache, caption mode, upload steps — one paragraph",
  "suggested_tags": ["5-8 YouTube tags from keyword research"]
}}
"""


def _slug(topic: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    return s[:80] or "topic"


def research_path(topic: str) -> Path:
    return settings.data_dir / "research" / f"{_slug(topic)}.json"


def save_research(research: ProductionResearch) -> Path:
    path = research_path(research.topic)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(research.to_dict(), indent=2), encoding="utf-8")
    return path


def load_research(topic: str) -> ProductionResearch | None:
    path = research_path(topic)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return ProductionResearch(
        topic=data.get("topic", topic),
        niche=data.get("niche", NICHE_POSITIONING),
        viewer_moment=data.get("viewer_moment", ""),
        emotional_stakes=data.get("emotional_stakes", ""),
        hook_angles=list(data.get("hook_angles") or []),
        script_beats=list(data.get("script_beats") or []),
        visual_framing=data.get("visual_framing", framing_notes_for_prompt()),
        competitor_gap=data.get("competitor_gap", ""),
        title_formula=data.get("title_formula", ""),
        jenny_citations=list(data.get("jenny_citations") or []),
        quality_notes=data.get("quality_notes", ""),
        researched_at=data.get("researched_at", ""),
        web_sources=list(data.get("web_sources") or []),
        competitor_titles=list(data.get("competitor_titles") or []),
        keyword_insights=list(data.get("keyword_insights") or []),
        recommended_path=data.get("recommended_path", ""),
        search_queries=list(data.get("search_queries") or []),
        research_sources=list(data.get("research_sources") or []),
    )


def _gather_external_context(topic: str) -> dict:
    """Web browse + Google Trends + YouTube API + vidIQ — all optional, best-effort."""
    sources: list[str] = []
    web_context = "(web research disabled)"
    competitor_context = "(no YouTube API — competitor search skipped)"
    keyword_context = "(no keyword data)"
    trends_context = "(Google Trends disabled or no data)"
    web_sources: list[dict] = []
    competitor_titles: list[str] = []
    keyword_insights: list[dict] = []
    search_queries: list[str] = []

    if settings.research_web_enabled:
        try:
            from shorts_bot.research.web_gather import gather_web_context

            web = gather_web_context(topic)
            block = web.context_block()
            if block:
                web_context = block
                sources.append("web_search")
                search_queries = web.queries
                web_sources = [
                    {"title": s.title, "url": s.url, "snippet": s.snippet[:300], "source": s.source}
                    for s in web.snippets
                ]
                if web.youtube_suggestions:
                    keyword_context = "YouTube autocomplete:\n" + "\n".join(
                        f"- {s}" for s in web.youtube_suggestions[:12]
                    )
                    sources.append("youtube_suggest")
        except Exception:
            web_context = "(web gather failed — continuing with course + LLM)"

    try:
        from shorts_bot.research.youtube_competitors import (
            competitor_context_block,
            search_competitor_shorts,
        )

        videos = search_competitor_shorts(topic)
        if videos:
            competitor_context = competitor_context_block(videos)
            competitor_titles = [v.title for v in videos]
            sources.append("youtube_api")
    except Exception:
        pass

    if settings.vidiq_enabled:
        try:
            from shorts_bot.research.vidiq import vidiq_keyword_lookup

            vidiq = vidiq_keyword_lookup(topic)
            if vidiq:
                block = vidiq.context_block()
                if block:
                    keyword_context = (keyword_context + "\n\n" + block).strip()
                    sources.append(vidiq.source or "vidiq")
                for kw in vidiq.keywords:
                    keyword_insights.append(
                        {
                            "keyword": kw.keyword,
                            "volume": kw.search_volume,
                            "competition": kw.competition,
                            "score": kw.overall_score,
                        }
                    )
        except Exception:
            pass

    if settings.google_trends_enabled:
        try:
            from shorts_bot.research.google_trends import fetch_google_trends

            trends = fetch_google_trends(topic)
            if trends:
                block = trends.context_block()
                if block:
                    trends_context = block
                    sources.append("google_trends")
                keyword_insights.extend(trends.to_insights())
        except Exception:
            pass

    return {
        "web_context": web_context,
        "competitor_context": competitor_context,
        "keyword_context": keyword_context,
        "trends_context": trends_context,
        "web_sources": web_sources,
        "competitor_titles": competitor_titles,
        "keyword_insights": keyword_insights,
        "search_queries": search_queries,
        "research_sources": sources,
    }


def _offline_research(topic: str, *, external: dict | None = None) -> ProductionResearch:
    ext = external or _gather_external_context(topic)
    path_note = (
        "Run: python3 -m shorts_bot.production.daily_cli "
        f"(topic cached in data/research/). CAPTION_MODE=ffmpeg. Upload via finish pipeline."
    )
    tags = [s.get("keyword", "") for s in ext.get("keyword_insights", []) if s.get("keyword")][:5]
    return ProductionResearch(
        topic=topic,
        niche=NICHE_POSITIONING,
        viewer_moment=f"The exact second before {topic} goes wrong.",
        emotional_stakes="They'll say something they'll regret or shut down completely.",
        hook_angles=[
            f"I used to wreck {topic} every time.",
            f"Right before {topic}, my chest would lock up.",
            f"One thing changed how I handle {topic}.",
        ],
        script_beats=[
            "Hook — personal struggle, ASAP",
            "Same loop — viewer recognizes themselves",
            "Turn — what I do now in the minute before",
            "One protocol — single concrete action",
            "Honest slip — still human",
            "Try tonight — low friction CTA",
            "Payoff — you're still here",
        ],
        visual_framing=framing_notes_for_prompt(),
        competitor_gap="Most Shorts give generic tips; miss the specific minute-before moment.",
        title_formula=f"Before {topic[:40]} — do this first #Shorts",
        jenny_citations=["Jenny 02 hook", "Jenny 05 safe zone framing", "Jenny 06 payoff"],
        quality_notes=quality_lessons(),
        researched_at=datetime.now(timezone.utc).isoformat(),
        web_sources=ext.get("web_sources", []),
        competitor_titles=ext.get("competitor_titles", []),
        keyword_insights=ext.get("keyword_insights", []),
        recommended_path=path_note,
        search_queries=ext.get("search_queries", []),
        research_sources=ext.get("research_sources", ["offline"]),
    )


def deep_research_topic(
    topic: str,
    *,
    force_refresh: bool = False,
    include_web: bool | None = None,
) -> ProductionResearch:
    """Deep research: web browse + vidIQ + YouTube competitors + LLM synthesis."""
    if not force_refresh:
        cached = load_research(topic)
        if cached and cached.viewer_moment:
            return cached

    use_web = settings.research_web_enabled if include_web is None else include_web
    external = _gather_external_context(topic) if use_web else {
        "web_context": "(skipped)",
        "competitor_context": "(skipped)",
        "keyword_context": "(skipped)",
        "trends_context": "(skipped)",
        "web_sources": [],
        "competitor_titles": [],
        "keyword_insights": [],
        "search_queries": [],
        "research_sources": [],
    }

    from shorts_bot.llm.provider import get_llm_backend

    backend = get_llm_backend()
    if backend is None:
        result = _offline_research(topic, external=external)
        save_research(result)
        return result

    prompt = _RESEARCH_PROMPT.format(
        niche_block=NICHE_POSITIONING,
        quality_lessons=quality_lessons(),
        web_context=external["web_context"],
        competitor_context=external["competitor_context"],
        keyword_context=external["keyword_context"],
        trends_context=external.get("trends_context", "(no trends data)"),
        topic=topic,
    )
    response = backend.client.chat.completions.create(
        model=backend.model,
        messages=[
            {"role": "system", "content": "Return valid JSON only. Ground answers in provided web/competitor data."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    payload = json.loads(response.choices[0].message.content or "{}")
    suggested_tags = [str(x).strip() for x in (payload.get("suggested_tags") or []) if str(x).strip()]
    for tag in suggested_tags:
        external["keyword_insights"].append({"keyword": tag, "volume": "", "competition": "", "score": "suggested"})

    result = ProductionResearch(
        topic=topic,
        niche=NICHE_POSITIONING,
        viewer_moment=str(payload.get("viewer_moment", "")).strip(),
        emotional_stakes=str(payload.get("emotional_stakes", "")).strip(),
        hook_angles=[str(x).strip() for x in (payload.get("hook_angles") or []) if str(x).strip()],
        script_beats=[str(x).strip() for x in (payload.get("script_beats") or []) if str(x).strip()],
        visual_framing=str(payload.get("visual_framing", "")).strip() or framing_notes_for_prompt(),
        competitor_gap=str(payload.get("competitor_gap", "")).strip(),
        title_formula=str(payload.get("title_formula", "")).strip(),
        jenny_citations=[str(x).strip() for x in (payload.get("jenny_citations") or []) if str(x).strip()],
        quality_notes=str(payload.get("quality_notes", "")).strip(),
        researched_at=datetime.now(timezone.utc).isoformat(),
        web_sources=external["web_sources"],
        competitor_titles=external["competitor_titles"],
        keyword_insights=external["keyword_insights"],
        recommended_path=str(payload.get("recommended_path", "")).strip(),
        search_queries=external["search_queries"],
        research_sources=external["research_sources"] + ["llm"],
    )
    save_research(result)
    return result
