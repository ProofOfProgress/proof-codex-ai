from __future__ import annotations

import json
from dataclasses import dataclass

from openai import OpenAI

from shorts_bot.brand.loader import ChannelBrand
from shorts_bot.config import settings
from shorts_bot.course.router import CourseRouter
from shorts_bot.drafts.hook_novelty import (
    check_hook_novelty,
    collect_recent_hooks,
    format_banned_hooks_block,
    hook_similarity,
)
from shorts_bot.drafts.quality import QualityReport, run_quality_checks
from shorts_bot.memory.agent_memory import AgentMemoryStore
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import Draft, MemoryStore
from shorts_bot.production.niche import NICHE_POSITIONING, quality_lessons
from shorts_bot.production.script_humanize import finalize_script


SYSTEM_PROMPT = f"""You write YouTube Shorts scripts (~25-35 seconds) for **AI / Tech** channel.

{NICHE_POSITIONING}

**Jenny Codex law:** curiosity hook FIRST (price shock or contrarian claim).

FORMAT (8 beats — conversational tool teaching, NOT Pay/Skip/Wait, NOT "who it's for"):
1. HOOK (0-2s): price shock, feature surprise, or what breaks — NOT "is X worth it?" or "I tested if"
2. SETUP: product name + what you'll learn
3. STRENGTH: one specific win (feature fact)
4. BUT: price, limit, or flaw
5. TRADEOFF: vs one competitor on one axis
6. PAYOFF: best tool fact last — viewer decides
7. Close: "Which tool next? Comment below."

TTS: say "Twitter" not "X" as a spoken word.
~70-110 words. Bold caption-friendly lines. 9:16 vertical. ONE named product only.

Return JSON: hook, script, help_angle (strength + weakness one-liner), visual_beats (6-8 — product UI, pricing, screen captures)."""


def _system_prompt(store: MemoryStore | None = None, *, draft_id: int | None = None) -> str:
    from shorts_bot.production.launch_phase import silent_launch_script_rules, would_be_silent_launch

    prompt = SYSTEM_PROMPT
    if would_be_silent_launch(store, draft_id=draft_id):
        prompt += silent_launch_script_rules()
    return prompt


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

    def _recent_hooks(self) -> list[str]:
        return collect_recent_hooks(self.store, self.memory)

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

    def _course_context(self, topic: str) -> str:
        base = f"AI/TECH SHORTS FORMAT:\n{NICHE_POSITIONING.strip()}\n\n{quality_lessons()}"
        if self.router:
            from shorts_bot.production.jenny_checks import jenny_retention_guidance

            base += f"\n\nRETENTION (Jenny Codex):\n{jenny_retention_guidance(topic)}"
        return base

    def _apply_ai_detection(
        self,
        topic: str,
        hook: str,
        script: str,
        help_angle: str,
        *,
        visual_beats: list[str] | None = None,
    ) -> GeneratedDraft:
        """Run AI detector loop until score ≤ threshold (~under 5% AI)."""
        finalized = finalize_script(topic, hook, script, help_angle)
        quality = run_quality_checks(
            topic=topic,
            script=finalized.script,
            hook=finalized.hook,
            help_angle=finalized.help_angle,
        )
        if not finalized.passed:
            quality = QualityReport(
                passed=False,
                issues=list(quality.issues)
                + [f"AI detector score {finalized.final_ai_score}/100 — need ≤{settings.ai_detect_threshold}"],
                warnings=quality.warnings,
            )
        return GeneratedDraft(
            topic=topic,
            hook=finalized.hook,
            script=finalized.script,
            help_angle=finalized.help_angle,
            quality=quality,
            visual_beats=visual_beats,
        )

    def generate(
        self,
        topic: str,
        angle: str | None = None,
        *,
        research=None,
    ) -> GeneratedDraft:
        if self.client is None:
            return self._generate_offline(topic, angle)

        course_ctx = self._course_context(topic)

        research_block = ""
        if research is not None:
            research_block = f"\n{research.draft_context()}\n"

        banned = format_banned_hooks_block(self._recent_hooks())
        if banned:
            research_block += f"\n{banned}\n"

        user_prompt = f"""Topic: {topic}
Optional angle: {angle or "none"}
{research_block}
{self._feedback_context()}

CHANNEL BRAND (AI / Tech — conversational; RTR/Ms. Byte retired):
{self.brand.draft_instructions()[:1800]}

HOOK RULES (Jenny 02 — critical):
- First line = price shock, feature surprise, or what breaks on the tool
- NEVER start with "Is X worth it?", "Everyone's paying for", "I tested if", or classroom intro
- NEVER use Pay / Skip / Wait stamps
- NEVER frame around buyer personas ("most shouldn't pay", "unless you code daily", "if your job is")

FORMAT RULES FOR THIS DRAFT:
{course_ctx}

Return JSON with keys:
- hook: first spoken line (curiosity FIRST — not host intro)
- script: full voiceover (25-35s when read aloud, 8 beats)
- help_angle: one sentence — main strength + main weakness
- visual_beats: list of 6-8 shots (product UI, pricing page, STRENGTH/WEAKNESS cards, screen captures)
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": _system_prompt(self.store)},
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
        return self._apply_ai_detection(
            topic, hook, script, help_angle, visual_beats=visual_beats or None
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
                "Fullscreen fixed CCTV hallway POV, night vision green, motion alert, distant silhouette, NO phone NO hands",
                "Fullscreen CCTV hallway cam, empty corridor night vision, REC overlay added in post",
                "Fullscreen CCTV hallway, tall figure closer in frame, grainy night vision, MOTION",
                "POV door deadbolt close-up, alarm clock on nightstand glowing 3:12 AM, NO phone",
                "Smart speaker nightstand, alarm clock LED visible, camera LED flicker, NO phone",
                "False calm: fullscreen CCTV empty hallway hold, quiet",
                "Fullscreen bedroom CCTV POV, figure at bed foot staring into lens, night vision green",
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
        elif "hallway" in lower and ("longer" in lower or "step" in lower):
            hook = "You counted the hallway tiles — there were three more than last night."
            script = (
                f"{hook} "
                "You walked it twice to be sure. The apartment felt the same size on the blueprint. "
                "You told yourself you were tired. At the far end, a door you never installed stood half-open. "
                "Cold air pushed out from a room that should be brick wall. "
                "You stepped back. The hallway stretched again while you watched. "
                "Something at the new end leaned into the light. Then it ran the whole length toward you."
            )
            help_angle = "Wrong place — hallway grows overnight; false calm miscount; spatial lunge scare."
            visual_beats = [
                "POV counting floor tiles in narrow apartment hallway, dim bulb",
                "Blueprint on table shows shorter hall — mismatch",
                "Impossible door at end of hall, half-open, cold haze",
                "Hallway visibly longer in single continuous shot",
                "False calm: empty stretched corridor hold",
                "Figure at far end leans into light",
                "Full sprint lunge down hallway toward camera",
            ]
        elif "basement" in lower or ("voice" in lower and "calling" in lower):
            hook = "Your own voice called your name from the basement — you hadn't gone down yet."
            script = (
                f"{hook} "
                "You stood at the top of the stairs. The bulb down there had been dead for months. "
                "You told yourself it was a recording. The voice said come down, exactly like you speak. "
                "You heard wet footsteps climbing toward you in the dark. "
                "You slammed the door. The handle turned from the other side. "
                "The voice whispered through the keyhole — already in the kitchen behind you."
            )
            help_angle = "Wrong sound — self-voice from sealed basement; false calm recording excuse; behind-you scare."
            visual_beats = [
                "Top of basement stairs, dead bulb, dark below",
                "Voice waveform on dusty recorder — your cadence",
                "Footsteps on wooden stairs in pitch black",
                "Door slam POV, trembling hand on knob",
                "False calm: silent closed door",
                "Kitchen over-shoulder — figure behind you in reflection of microwave door",
                "Face lunge from behind into lens",
            ]
        elif "mirror" in lower or "reflection" in lower or "blink" in lower:
            hook = "Your reflection waved before you moved your hand."
            script = (
                f"{hook} "
                "You froze in the bathroom. The glass showed you still, arm raised without you raising it. "
                "You told yourself it was latency on the cheap mirror. You switched off the light. "
                "The reflection stayed lit in the dark. It mouthed your name with your voice. "
                "You backed into the hallway. The mirror slid across the wall on its own. "
                "It filled the doorway. Then the glass shattered outward at your face."
            )
            help_angle = "Wrong reflection — independent wave; false calm latency; glass lunge scare."
            visual_beats = [
                "Bathroom mirror, your still body, reflection arm raised early",
                "Lights off — reflection still illuminated",
                "Reflection mouths name — sync wrong",
                "Mirror slides along wall toward hallway",
                "False calm: cracked still frame",
                "Glass shatters toward camera full frame",
            ]
        elif "bed" in lower or "sheets" in lower or "sat on" in lower:
            hook = "The dip in your mattress was still warm — you sleep alone."
            script = (
                f"{hook} "
                "You hadn't gotten into bed yet. You told yourself the heating was uneven. "
                "You pulled back the sheet. Four long indents, like fingers, pressed through the foam. "
                "You heard breathing from the closet you keep empty. "
                "You stepped back. The blankets lifted as if someone stood up under them. "
                "A shape rose at full height. It lunged across the room."
            )
            help_angle = "Wrong place — warm indent without guest; false calm heating; bedsheet lunge scare."
            visual_beats = [
                "Mattress indent close-up, steam-warm glow",
                "Finger-shaped depressions in foam",
                "Empty closet door breathing fog",
                "Blankets lift vertical silhouette",
                "False calm: sheets settle",
                "Full-body lunge from bed toward camera",
            ]
        elif "elevator" in lower or "floor" in lower and "exist" in lower:
            hook = "The elevator opened on a floor that isn't on the panel."
            script = (
                f"{hook} "
                "You live on four. The display read B. You told yourself maintenance added a level. "
                "The hall outside was your building, but every door was numbered backward. "
                "Your apartment label hung on the wrong side. You heard your keys jingle behind you. "
                "You turned. Another you walked out of your unit smiling. "
                "It sprinted down the impossible hall and tackled the lens."
            )
            help_angle = "Wrong place — impossible floor; false calm maintenance; doppelgänger lunge scare."
            visual_beats = [
                "Elevator doors open on unlabeled floor B",
                "Hallway identical but reversed door numbers",
                "Your door on wrong wall",
                "Doppelgänger exits your unit with your keys",
                "False calm: empty reversed hall",
                "Sprint tackle into camera",
            ]
        else:
            hook, script, help_angle, visual_beats = self._offline_fallback_for_topic(topic, angle)
        return self._apply_ai_detection(
            topic, hook, script, help_angle, visual_beats=visual_beats
        )

    def _offline_fallback_for_topic(
        self, topic: str, angle: str | None
    ) -> tuple[str, str, str, list[str]]:
        """Topic-tied offline fallback — never default to mirror-blink recycle."""
        lower = topic.lower()
        recent = self._recent_hooks()
        candidates: list[tuple[str, str, str, list[str]]] = []

        def add(hook: str, script: str, help_angle: str, beats: list[str]) -> None:
            if check_hook_novelty(hook, recent).novel:
                candidates.append((hook, script, help_angle, beats))

        if "monitor" in lower or "heartbeat" in lower:
            add(
                "The baby monitor showed an empty crib — the audio had two heartbeats.",
                (
                    "The baby monitor showed an empty crib — the audio had two heartbeats. "
                    "You told yourself interference. The waveform synced perfectly — yours and another. "
                    "You muted the speaker. The second beat kept counting in the room. "
                    "You looked at the crib on screen. A small hand pressed the lens from inside. "
                    "Then the monitor face filled with teeth."
                ),
                "Wrong sound — dual heartbeat on empty crib; false calm interference; monitor lunge.",
                [
                    "Baby monitor split screen: empty crib, dual heartbeat graph",
                    "Mute button — second pulse audible in room",
                    "Hand on monitor lens from inside crib feed",
                    "False calm: static crib view",
                    "Monitor screen teeth lunge full frame",
                ],
            )
        if "speaker" in lower or "smart" in lower:
            add(
                "Your smart speaker answered a question you never asked.",
                (
                    "Your smart speaker answered a question you never asked. "
                    "It quoted your childhood address — out loud, in your mother's voice. "
                    "You unplugged it. The LED stayed on. "
                    "It whispered from inside the wall. "
                    "You tore the outlet plate. Something smiled in the wiring. "
                    "It lunged through the drywall at your face."
                ),
                "Wrong sound — unprompted answer; false calm unplug; wall lunge scare.",
                [
                    "Smart speaker glowing, wrong LED pulse",
                    "Unplugged cord — LED still on",
                    "Voice from inside wall cavity",
                    "Outlet plate torn — face in wires",
                    "Drywall burst lunge toward camera",
                ],
            )
        if "teeth" in lower or "apple" in lower:
            add(
                "There were bite marks on the apple — from the inside.",
                (
                    "There were bite marks on the apple — from the inside. "
                    "You hadn't cut it open. You told yourself it was bruising. "
                    "The skin pushed outward like something chewed from within. "
                    "You dropped it. The apple rolled and split on its own. "
                    "Something small crawled out smiling. It leapt at the lens."
                ),
                "Wrong place — impossible interior bite; false calm bruise; creature lunge.",
                [
                    "Apple on counter, outward teeth impressions",
                    "Skin bulges from inside",
                    "Apple splits rolling on tile",
                    "Small figure crawls out",
                    "Leap lunge to camera",
                ],
            )

        add(
            f"The {topic.split('—')[0].strip().rstrip('.')} — and then the lights died.",
            (
                f"You noticed {topic.rstrip('.')}. "
                "You told yourself there was a rational explanation. "
                "Every screen in the apartment refreshed with the same timestamp — one that hasn't happened yet. "
                "You heard movement in the room you just left. "
                "You turned back. The doorway held something that learned your posture. "
                "It charged the moment you exhaled."
            ),
            f"Anthology dread tied to topic — false calm rationalization; doorway lunge on {topic}.",
            [
                f"Establishing shot: {topic[:60]}, liminal apartment",
                "All screens same impossible timestamp",
                "Doorway silhouette mirrors your stance",
                "False calm: hold on empty room",
                "Charge lunge through doorway",
            ],
        )

        for hook, script, help_angle, beats in candidates:
            return hook, script, help_angle, beats

        # Last resort: topic-embedded hook (still not mirror-blink template).
        hook = f"{topic[0].upper()}{topic[1:80].rstrip('.')} — you weren't supposed to notice yet."
        script = (
            f"{hook} "
            "You froze. You told yourself you were overtired. "
            "The detail got worse the longer you stared. "
            "You reached for your phone and the camera showed the room without you in it. "
            "You looked up. Whatever you noticed was already beside you. "
            "It lunged when you blinked."
        )
        return (
            hook,
            script,
            f"Topic-native hook — earned lunge on {topic}.",
            [
                f"Wide shot establishing: {topic[:50]}",
                "Detail worsens — slow push in",
                "Phone camera shows empty room",
                "Entity beside you over-shoulder",
                "Lunge on blink",
            ],
        )

    def create_and_store(self, topic: str, angle: str | None = None, *, research=None) -> Draft:
        recent = self._recent_hooks()
        generated: GeneratedDraft | None = None
        for attempt in range(5):
            candidate = self.generate(topic, angle, research=research)
            report = check_hook_novelty(candidate.hook, recent)
            if report.novel:
                generated = candidate
                break
            # Offline/LLM recycled a hook — nudge angle and retry.
            angle = f"Fresh hook required (attempt {attempt + 2}): {report.reason}"
        if generated is None:
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
