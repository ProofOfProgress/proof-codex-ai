"""Map script lines to stick-figure scenes + speech bubbles."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class Pose(str, Enum):
    LYING_AWAKE = "lying_awake"
    REACHING_PHONE = "reaching_phone"
    PUTTING_PHONE_DOWN = "putting_phone_down"
    NAMING_THOUGHT = "naming_thought"
    BREATHING = "breathing"
    CALM_IN_BED = "calm_in_bed"
    STANDING_CALM = "standing_calm"
    POINTING_SELF = "pointing_self"
    THINKING = "thinking"
    HUDDLED = "huddled"
    WALKING = "walking"


@dataclass
class ScenePlan:
    spoken_text: str
    pose: Pose
    bubble_text: str | None  # None = show action only (narrator VO)
    prop: str | None = None


_AI_PHRASES = (
    "in today's",
    "it's important to note",
    "delve",
    "tapestry",
    "landscape",
    "furthermore",
    "moreover",
    "in conclusion",
    "game-changer",
    "unlock",
    "leverage",
    "dive in",
    "navigate",
)


def extract_quoted_dialogue(text: str) -> str | None:
    m = re.search(r"'([^']+)'|\"([^\"]+)\"", text)
    if m:
        return (m.group(1) or m.group(2) or "").strip()
    return None


def _pose_from_beat_hint(beat: str) -> Pose | None:
    """Map draft visual_beat description to a pose when keywords match."""
    lower = beat.lower()
    if any(w in lower for w in ("bathroom", "stall", "cry", "hide", "huddle")):
        return Pose.HUDDLED
    if any(w in lower for w in ("walk", "excuse", "leave", "door")):
        return Pose.WALKING
    if any(w in lower for w in ("breath", "breathe", "calm", "reset")):
        return Pose.BREATHING
    if any(w in lower for w in ("phone", "scroll")):
        return Pose.REACHING_PHONE
    if any(w in lower for w in ("point", "try this", "gesture")):
        return Pose.POINTING_SELF
    if any(w in lower for w in ("think", "overwhelm", "spiral")):
        return Pose.THINKING
    return None


def plan_scene(spoken_text: str, *, beat_hint: str | None = None) -> ScenePlan:
    t = spoken_text.strip()
    lower = t.lower()
    bubble = extract_quoted_dialogue(t)

    if beat_hint:
        hinted = _pose_from_beat_hint(beat_hint)
        if hinted:
            prop = "stall" if hinted == Pose.HUDDLED else None
            return ScenePlan(t, hinted, bubble, prop)

    if bubble:
        return ScenePlan(t, Pose.NAMING_THOUGHT, bubble, "thought")
    if any(w in lower for w in ("bathroom", "stall", "cry", "hide in")):
        return ScenePlan(t, Pose.HUDDLED, bubble, "stall")
    if "overwhelm" in lower or "heart pound" in lower:
        return ScenePlan(t, Pose.HUDDLED, None, "stall")
    if "excuse myself" in lower or "walk to" in lower or "close the" in lower:
        return ScenePlan(t, Pose.WALKING, None, "door")
    if "shoulder roll" in lower or "release tension" in lower:
        return ScenePlan(t, Pose.BREATHING, None, None)
    if "office" in lower or "work" in lower:
        return ScenePlan(t, Pose.THINKING, None, "desk")
    if "phone" in lower and ("before" in lower or "reach" in lower):
        return ScenePlan(t, Pose.PUTTING_PHONE_DOWN, None, "phone")
    if "phone" in lower or "scrolling" in lower:
        return ScenePlan(t, Pose.REACHING_PHONE, None, "phone")
    if "3 am" in lower or "3am" in lower or "brain" in lower or "laps" in lower:
        return ScenePlan(t, Pose.LYING_AWAKE, None, "clock")
    if "breathe" in lower or "breath" in lower or "seconds in" in lower:
        return ScenePlan(t, Pose.BREATHING, None, None)
    if "name" in lower and "thought" in lower:
        return ScenePlan(t, Pose.NAMING_THOUGHT, "I'm thinking about tomorrow.", "thought")
    if "three times" in lower or "do it" in lower:
        return ScenePlan(t, Pose.BREATHING, None, None)
    if "nervous system" in lower or "rhythm" in lower:
        return ScenePlan(t, Pose.BREATHING, None, None)
    if "dark" in lower or "room" in lower:
        return ScenePlan(t, Pose.CALM_IN_BED, None, None)
    if "day can wait" in lower or lower.endswith("tonight."):
        return ScenePlan(t, Pose.STANDING_CALM, None, None)
    if "try this" in lower:
        return ScenePlan(t, Pose.POINTING_SELF, None, None)
    if "walk" in lower or "party" in lower or "door" in lower:
        return ScenePlan(t, Pose.STANDING_CALM, None, None)
    return ScenePlan(t, Pose.THINKING, None, None)


def ai_likelihood_score(text: str) -> int:
    """0 = human-like, 100 = obvious AI. Local heuristic (no API)."""
    lower = text.lower()
    score = 0
    words = text.split()
    if len(words) < 20:
        score += 15
    for phrase in _AI_PHRASES:
        if phrase in lower:
            score += 12
    # Low contraction density
    contractions = len(re.findall(r"\b\w+'\w+\b", text))
    if len(words) > 30 and contractions < 2:
        score += 20
    # Uniform sentence length
    sents = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    if len(sents) >= 3:
        lengths = [len(s.split()) for s in sents]
        if max(lengths) - min(lengths) < 4:
            score += 15
    if "—" in text:
        score += 5
    return min(100, score)
