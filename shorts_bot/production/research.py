"""Deep research before draft — niche fit, hooks, framing (Jenny 05), competitor gaps."""

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
        }

    def draft_context(self) -> str:
        hooks = "\n".join(f"- {h}" for h in self.hook_angles[:4])
        beats = "\n".join(f"- {b}" for b in self.script_beats[:6])
        cites = ", ".join(self.jenny_citations) or "Jenny 02 hook, 05 mute-safe framing, 06 retention"
        return f"""DEEP RESEARCH (use this — do not genericize):
Niche: {self.niche}
Viewer moment: {self.viewer_moment}
Stakes: {self.emotional_stakes}
Competitor gap: {self.competitor_gap}
Title formula: {self.title_formula}

Hook angles (pick strongest):
{hooks}

Script beats (hook → momentum → payoff):
{beats}

Visual framing: {self.visual_framing}
Jenny course refs: {cites}
Quality bar: {self.quality_notes}
"""


_RESEARCH_PROMPT = """You are a YouTube Shorts production researcher for faceless self-help channel Soft Continuity.

NICHE POSITIONING:
{niche_block}

QUALITY LESSONS (what performed better vs worse on this channel):
{quality_lessons}

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
  "competitor_gap": "what faceless Shorts miss on this topic",
  "title_formula": "helpful title pattern, not rage-bait",
  "jenny_citations": ["Jenny 05", "Jenny 06"],
  "quality_notes": "how to beat generic sleep/anxiety slop on this topic"
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
    )


def _offline_research(topic: str) -> ProductionResearch:
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
    )


def deep_research_topic(topic: str, *, force_refresh: bool = False) -> ProductionResearch:
    """Run Gemini/OpenAI research for a topic; cache to data/research/."""
    if not force_refresh:
        cached = load_research(topic)
        if cached and cached.viewer_moment:
            return cached

    from shorts_bot.llm.provider import get_llm_backend

    backend = get_llm_backend()
    if backend is None:
        result = _offline_research(topic)
        save_research(result)
        return result

    prompt = _RESEARCH_PROMPT.format(
        niche_block=NICHE_POSITIONING,
        quality_lessons=quality_lessons(),
        topic=topic,
    )
    response = backend.client.chat.completions.create(
        model=backend.model,
        messages=[
            {"role": "system", "content": "Return valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    payload = json.loads(response.choices[0].message.content or "{}")
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
    )
    save_research(result)
    return result
