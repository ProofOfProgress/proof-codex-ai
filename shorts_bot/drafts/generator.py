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
from shorts_bot.production.niche import NICHE_POSITIONING, quality_lessons
from shorts_bot.production.world import world_lore_for_scripts


SYSTEM_PROMPT = f"""You write faceless YouTube horror Shorts for Don't Blink (~25-35 seconds).

{world_lore_for_scripts()}

CHANNEL VOICE: Second-person scary story — "you" notice something that should not be real. Tense, specific, not cosy.
No self-help, no first-person therapy, no "hey guys", no creepypasta listicles.

STRUCTURE (earn the jumpscare — write backwards from final scare):
- Line 1 = hook (timestamp glitch, wrong reflection, text from dead contact)
- Beats 2-4 (3-12s): establish normal, then fracture it — new wrong detail each line
- Beats 5-6 (12-20s): escalation — sound + visual micro-cues
- Beat 7 (20-26s): FALSE CALM — "you told yourself it was nothing" / quiet dread, bait the swipe
- JUMPSCARE ROULETTE: timing varies per video — place the scare line where the plan says (early / mid / late / double-tap fake+real). Viewer must NOT predict the hit.
- Every script still needs ONE clear jumpscare cue (lunge, slam, lens fill) on the primary scare line — then STOP or brief dread coda, no explanation
- Mute-safe: 6-8 visual_beats (one cinematic horror shot per beat, AI full-motion)
- Singular "you". ~70-110 words spoken. 9:16 faceless horror.

Return JSON: hook, script, help_angle (one sentence: scare type + why the hook feels wrong), visual_beats (6-8 horror scene descriptions)."""


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

    def _horror_course_context(self, topic: str) -> str:
        base = f"HORROR FORMAT (Don't Blink):\n{NICHE_POSITIONING.strip()}\n\n{quality_lessons()}"
        if self.router:
            from shorts_bot.production.jenny_checks import jenny_retention_guidance

            base += f"\n\nRETENTION (Jenny-adapted for horror):\n{jenny_retention_guidance(topic)}"
        return base

    def generate(
        self,
        topic: str,
        angle: str | None = None,
        *,
        research=None,
    ) -> GeneratedDraft:
        if self.client is None:
            return self._generate_offline(topic, angle)

        course_ctx = self._horror_course_context(topic)

        research_block = ""
        if research is not None:
            research_block = f"\n{research.draft_context()}\n"

        user_prompt = f"""Topic: {topic}
Optional angle: {angle or "none"}
{research_block}
{self._feedback_context()}

CHANNEL BRAND (Don't Blink — terrifying faceless horror, jumpscare at end):
{self.brand.draft_instructions()[:1800]}

ENDING RULE: Final spoken line cues the jumpscare, then STOP. No explanation after the scare.
Do NOT end with channel taglines ("watch the whole thing") — those are metadata only, not voiceover.
Do NOT use cosy self-help tone, stick figures, or generic "scary story #12" framing.

FORMAT RULES FOR THIS DRAFT:
{course_ctx}

Return JSON with keys:
- hook: first spoken line (something clearly wrong)
- script: full voiceover script (25-35s when read aloud)
- help_angle: one sentence — scare type (reflection/knock/glitch/lunge) + why the hook feels wrong
- visual_beats: list of 6-8 cinematic horror shot descriptions (mute-friendly, one per beat)
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.85,
        )
        payload = json.loads(response.choices[0].message.content or "{}")
        hook = str(payload.get("hook", "")).strip()
        script = str(payload.get("script", "")).strip()
        help_angle = str(payload.get("help_angle", "")).strip()
        beats_raw = payload.get("visual_beats") or []
        visual_beats = [str(b).strip() for b in beats_raw if str(b).strip()][:8]
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
        lower = topic.lower()
        if "security" in lower or "camera" in lower or "motion" in lower:
            hook = "Your security camera flagged motion at 3:12 AM — you live alone."
            script = (
                f"{hook} "
                "You opened the app. The hallway was empty. You told yourself it was a glitch. "
                "You refreshed the feed. The figure was closer. You checked the locks — all sealed. "
                "You heard a soft tap from the speaker. The live view updated. "
                "Something stood at the bottom of your bed, staring into the lens. "
                "It smiled. Then it lunged at the camera."
            )
            help_angle = "Wrong place — security cam motion while alone; false calm glitch excuse; lens lunge scare."
            visual_beats = [
                "Phone screen: security app motion alert 3:12 AM, dark apartment",
                "Live feed hallway empty — timestamp overlay",
                "Refresh: tall figure closer in frame, grainy night vision",
                "POV checking door locks, chain still on",
                "Speaker tap — camera LED flickers",
                "False calm: empty hallway hold, quiet",
                "Figure at bed foot staring into camera, night vision green",
                "Full-frame lunge into lens, screen glitch",
            ]
        elif "text" in lower or "delivered" in lower or "message" in lower:
            hook = "The last text showed delivered — but their phone was off."
            script = (
                f"{hook} "
                "You stared at the screen. No typing bubble. You called anyway — straight to voicemail. "
                "You told yourself the app lagged. A new message appeared: I can see you. "
                "You checked the window. Nothing. Your phone lit up again from inside the dark hallway. "
                "The message read: behind you. Then the screen showed your own face screaming."
            )
            help_angle = "Wrong text — delivered while phone off; false calm app lag; screen-face jumpscare."
            visual_beats = [
                "Phone lock screen: delivered receipt, contact name, 3am",
                "Call failed — phone off icon",
                "New message slides in: I can see you",
                "Window reflection empty",
                "Phone glows in dark hallway on its own",
                "False calm: static chat screen",
                "Screen morphs to your face screaming full frame",
            ]
        elif "photo" in lower or "timestamp" in lower or "next week" in lower:
            hook = "The photo timestamp says next Tuesday — you took it tonight."
            script = (
                f"{hook} "
                "You opened the gallery. The room in the shot was your kitchen, lights off. "
                "You told yourself the clock was wrong. You checked the calendar on the fridge — today. "
                "You zoomed in. Your own back was in the frame, facing the stove. "
                "You were not in the kitchen. You heard a shutter click behind you. "
                "You turned. The phone in your hand showed a new photo — taken from inside the closet."
            )
            help_angle = "Wrong time — future timestamp on fresh photo; false calm clock glitch; closet POV scare."
            visual_beats = [
                "Phone gallery: photo thumbnail, timestamp next Tuesday overlay",
                "Kitchen dark in photo, you in bedroom POV",
                "Fridge calendar today — mismatch",
                "Zoom: your back in frame facing stove",
                "Shutter click sound cue — hallway still",
                "False calm: static phone screen",
                "New photo notification — taken from closet angle",
                "Closet POV fills frame toward your face",
            ]
        elif "knock" in lower or "closet" in lower:
            hook = "The knock came from inside the closet you never open."
            script = (
                f"{hook} "
                "You froze. You told yourself it was the house settling. "
                "You pressed your ear to the door. Three slow knocks answered from inside. "
                "You backed away. The handle turned by itself. "
                "You whispered that nobody was home. The closet door cracked open. "
                "A hand reached out. Then the whole thing lunged into the hallway."
            )
            help_angle = "Wrong sound — knock from sealed closet; false calm settling; door lunge scare."
            visual_beats = [
                "Bedroom closet door, never opened, dim lamp",
                "Ear to door — muffled knock from inside",
                "Handle turns slowly",
                "Crack of door, darkness within",
                "False calm: door still, quiet",
                "Hand reaches from closet slit",
                "Full-body lunge into hallway toward camera",
            ]
        else:
            hook = "You blinked at the mirror — your reflection blinked one second later."
            script = (
                f"{hook} "
                "You stepped closer and the glass stayed still, but the eyes in it didn't. "
                "You raised your phone to record proof and the screen showed an empty bathroom. "
                "You looked up — the reflection was already facing the door behind you. "
                "The hallway light flickered off. "
                "You told yourself it was a lag, a trick of tired eyes. "
                "You turned to leave. "
                f"{(angle or 'The thing in the mirror opened its mouth the moment you looked away')}."
            )
            help_angle = (
                f"Wrong-reflection jumpscare — impossible timing on {topic} hooks viewers who trust mirrors."
            )
            visual_beats = [
                "POV bathroom mirror, cold blue light, your silhouette facing glass",
                "Reflection eyes blink delayed — one frame wrong",
                "Phone screen recording shows empty room while mirror still has figure",
                "Reflection turned toward hallway door you have not opened yet",
                "Hallway light dies — long dark corridor, slow drift",
                "False calm: static mirror, quiet hold, empty frame",
                "Full-frame face lunge from mirror surface toward camera",
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
