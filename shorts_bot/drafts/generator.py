from __future__ import annotations

import json
from dataclasses import dataclass

from openai import OpenAI

from shorts_bot.brand.loader import ChannelBrand
from shorts_bot.config import settings
from shorts_bot.course.router import CourseRouter
from shorts_bot.drafts.quality import QualityReport, run_quality_checks
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import Draft, MemoryStore


SYSTEM_PROMPT = """You write faceless YouTube Shorts scripts using ONLY the Jenny Hoyos course rules provided.
Rules:
- Idea and hook are linked. Start with shock or immediate curiosity. Start the video ASAP.
- Every line moves toward payoff. End promptly after resolution.
- Video must work on mute — write visual beats, not just voiceover mush.
- CTA before payoff if included (subscribe ask right before highest attention).
- No slop, no filler, no generic motivation spam. Must genuinely help people.
- 9:16 Short, ~30-45 seconds spoken. Faceless.
- Return valid JSON only with keys: hook, script, help_angle, visual_beats (list of 3-5 shot descriptions)."""


@dataclass
class GeneratedDraft:
    topic: str
    hook: str
    script: str
    help_angle: str
    quality: QualityReport


class DraftGenerator:
    def __init__(
        self,
        store: MemoryStore,
        client: OpenAI | None = None,
        router: CourseRouter | None = None,
        memory: MemoryExtensions | None = None,
        brand: ChannelBrand | None = None,
    ) -> None:
        self.store = store
        self.client = client
        self.router = router
        self.memory = memory
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
        return "\n\n".join(parts) if parts else "No approval history yet."

    def generate(self, topic: str, angle: str | None = None) -> GeneratedDraft:
        if self.client is None:
            return self._generate_offline(topic, angle)

        course_ctx = ""
        if self.router:
            course_ctx = self.router.build_guidance(f"draft script hook retention payoff {topic}")

        user_prompt = f"""Topic: {topic}
Optional angle: {angle or "none"}

{self._feedback_context()}

CHANNEL BRAND (Soft Continuity — warm help, one subtle oracle line in script):
{self.brand.draft_instructions()[:1800]}

JENNY COURSE RULES FOR THIS DRAFT:
{course_ctx}

Return JSON with keys:
- hook: first spoken line
- script: full voiceover script
- help_angle: one sentence on who this helps and how
- visual_beats: list of 3-5 visual shot descriptions (mute-friendly)
"""
        response = self.client.chat.completions.create(
            model=settings.openai_model,
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
        quality = run_quality_checks(topic=topic, script=script, hook=hook, help_angle=help_angle)
        return GeneratedDraft(topic=topic, hook=hook, script=script, help_angle=help_angle, quality=quality)

    def _generate_offline(self, topic: str, angle: str | None) -> GeneratedDraft:
        hook = f"Stop scrolling — this one habit around {topic} actually helps."
        script = (
            f"{hook} "
            f"If you're dealing with {topic}, here's the part most Shorts skip. "
            f"{(angle or 'Focus on one small action you can do today')}. "
            f"Do it once, notice what changes, then repeat tomorrow. "
            f"This works on the days you don't believe it. "
            f"You're still here. Good."
        )
        help_angle = f"Helps people struggling with {topic} take one concrete step today."
        quality = run_quality_checks(topic=topic, script=script, hook=hook, help_angle=help_angle)
        return GeneratedDraft(topic=topic, hook=hook, script=script, help_angle=help_angle, quality=quality)

    def create_and_store(self, topic: str, angle: str | None = None) -> Draft:
        generated = self.generate(topic, angle)
        notes = generated.quality.summary()
        if self.router:
            route = self.router.route(topic)
            notes = f"{notes} | Lever: {route.main_lever}"
        return self.store.save_draft(
            topic=generated.topic,
            script=generated.script,
            hook=generated.hook,
            help_angle=generated.help_angle,
            quality_notes=notes,
        )
