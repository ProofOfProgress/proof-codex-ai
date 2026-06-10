from __future__ import annotations

import json
from dataclasses import dataclass

from openai import OpenAI

from shorts_bot.brand.loader import ChannelBrand
from shorts_bot.config import settings
from shorts_bot.course.router import CourseRouter
from shorts_bot.drafts.quality import QualityReport, run_quality_checks
from shorts_bot.memory.agent_memory import AgentMemoryStore
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import Draft, MemoryStore


SYSTEM_PROMPT = """You write faceless YouTube Shorts using ONLY Jenny Hoyos course rules.

CHANNEL VOICE: A real faceless creator — same struggles as the viewer, sharing what helped THEM (first person: I, my, I used to).

JENNY RULES:
- Idea ↔ hook linked. Shock/curiosity hook. Start video ASAP — no warm-up.
- Every line → payoff. Cause-and-effect (but/so). End right after payoff.
- Mute-safe: 3-5 visual_beats (stick figure actions per beat).
- Singular "you". CTA before payoff if subscribe mention.
- No slop, no "hey guys", no guru lecture mode.
- ~30-45 seconds spoken. 9:16 faceless.

Return JSON: hook, script, help_angle, visual_beats (list of 3-5 stick-figure scene descriptions)."""


@dataclass
class GeneratedDraft:
    topic: str
    hook: str
    script: str
    help_angle: str
    quality: QualityReport
    visual_beats: list[str] | None = None


class DraftGenerator:
    def __init__(
        self,
        store: MemoryStore,
        client: OpenAI | None = None,
        model: str | None = None,
        router: CourseRouter | None = None,
        memory: MemoryExtensions | None = None,
        agent_memory: AgentMemoryStore | None = None,
        brand: ChannelBrand | None = None,
    ) -> None:
        self.store = store
        self.client = client
        self.model = model or settings.openai_model
        self.router = router
        self.memory = memory
        self.agent_memory = agent_memory
        self.brand = brand or ChannelBrand()

    def _feedback_context(self) -> str:
        rejections = self.store.rejection_summary()[:8]
        approvals = self.store.approval_summary()[:5]
        parts = []
        if self.memory:
            training = self.memory.applied_training_context()
            if training:
                parts.append(training)
        if rejections:
            parts.append("Recent rejections to avoid repeating:\n" + "\n".join(f"- {r}" for r in rejections))
        if approvals:
            parts.append("Recent approvals to learn from:\n" + "\n".join(f"- {a}" for a in approvals))
        if self.agent_memory:
            block = self.agent_memory.context_block(max_chars=2000)
            if block:
                parts.append(block)
        return "\n\n".join(parts) if parts else "No approval history yet."

    def generate(
        self,
        topic: str,
        angle: str | None = None,
        *,
        research=None,
    ) -> GeneratedDraft:
        if self.client is None:
            return self._generate_offline(topic, angle)

        course_ctx = ""
        if self.router:
            from shorts_bot.production.jenny_checks import jenny_draft_guidance

            course_ctx = jenny_draft_guidance(topic)

        research_block = ""
        if research is not None:
            research_block = f"\n{research.draft_context()}\n"

        user_prompt = f"""Topic: {topic}
Optional angle: {angle or "none"}
{research_block}
{self._feedback_context()}

CHANNEL BRAND (Soft Continuity — warm help, first-person):
{self.brand.draft_instructions()[:1800]}

ENDING RULE: Stop right after the payoff (one concrete action landed). Do NOT end the script with
"you're still here" / "you're still here. good." — that tagline is channel metadata only, not voiceover.

JENNY COURSE RULES FOR THIS DRAFT:
{course_ctx}

Return JSON with keys:
- hook: first spoken line
- script: full voiceover script
- help_angle: one sentence on who this helps and how
- visual_beats: list of 3-5 visual shot descriptions (mute-friendly)
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.8,
        )
        payload = json.loads(response.choices[0].message.content or "{}")
        hook = str(payload.get("hook", "")).strip()
        script = str(payload.get("script", "")).strip()
        help_angle = str(payload.get("help_angle", "")).strip()
        beats_raw = payload.get("visual_beats") or []
        visual_beats = [str(b).strip() for b in beats_raw if str(b).strip()][:6]
        quality = run_quality_checks(topic=topic, script=script, hook=hook, help_angle=help_angle)
        return GeneratedDraft(
            topic=topic,
            hook=hook,
            script=script,
            help_angle=help_angle,
            quality=quality,
            visual_beats=visual_beats or None,
        )

    def _generate_offline(self, topic: str, angle: str | None) -> GeneratedDraft:
        hook = f"I used to lose sleep over {topic}. Same loop every night."
        script = (
            f"{hook} "
            f"So here's what I do now before I make it worse. "
            f"{(angle or 'One small thing that actually helped me')}. "
            f"I still slip sometimes — but this shortens the spiral. "
            f"Try it once tonight — one breath before {topic}."
        )
        help_angle = f"I share what helped me with {topic} — for anyone in the same loop."
        visual_beats = [
            f"stick figure stressed about {topic}",
            "taking one slow breath",
            "small calm gesture — try this",
        ]
        quality = run_quality_checks(topic=topic, script=script, hook=hook, help_angle=help_angle)
        return GeneratedDraft(
            topic=topic,
            hook=hook,
            script=script,
            help_angle=help_angle,
            quality=quality,
            visual_beats=visual_beats,
        )

    def create_and_store(self, topic: str, angle: str | None = None, *, research=None) -> Draft:
        generated = self.generate(topic, angle, research=research)
        notes = generated.quality.summary()
        if self.router:
            route = self.router.route(topic)
            notes = f"{notes} | Lever: {route.main_lever}"
        draft = self.store.save_draft(
            topic=generated.topic,
            script=generated.script,
            hook=generated.hook,
            help_angle=generated.help_angle,
            quality_notes=notes,
        )
        if generated.visual_beats:
            from shorts_bot.drafts.meta import save_draft_meta

            save_draft_meta(draft.id, visual_beats=generated.visual_beats)
        return draft
