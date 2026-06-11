"""Jenny Hoyos retention rules adapted for Don't Blink horror Shorts."""

from __future__ import annotations

import re

from shorts_bot.course.loader import CourseKnowledgeBase
from shorts_bot.config import settings


_SECOND_PERSON = re.compile(
    r"\b(you|you're|you've|you'd|your|yours)\b",
    re.I,
)
_FIRST_PERSON = re.compile(
    r"\b(i|i'm|i've|i'd|my|me|same here|i used to|honestly|look)\b",
    re.I,
)


def jenny_retention_guidance(topic: str) -> str:
    """Hook/retention rules adapted for Don't Blink horror (not cosy self-help)."""
    return f"""Topic: {topic}
- Hook line 1 = impossible detail (not "scary story #N")
- Start video immediately — no warm-up, no channel intro
- Every beat adds a worse wrong detail (but/so cause-effect)
- False calm beat before final scare — quiet VO bait
- Payoff = jumpscare cue in final line, then stop (no explanation)
- Mute-safe: each beat must read as a distinct horror shot
- Singular "you"; captions in upper safe zone (Jenny 05)
"""


def jenny_draft_guidance(topic: str) -> str:
    from shorts_bot.course.router import CourseRouter

    kb = CourseKnowledgeBase(settings.course_dir)
    r = CourseRouter(kb)
    guidance = r.build_guidance(
        f"faceless short personal storyteller struggles what helped me "
        f"idea hook visual mute retention payoff relatability singular you {topic}"
    )
    return f"JENNY COURSE (enforce hook→momentum→payoff, mute-safe visuals, singular you):\n{guidance}\n"


HORROR_SCRIPT_RULES = """
VOICE — immersive second-person horror (Jenny 02 + 06 adapted):
- Singular "you" — viewer is inside the scene
- Contractions, mixed sentence lengths; no lecture mode
- No "hey guys" / plural audience

STRUCTURE (Jenny 02 + 06):
- Hook ASAP — impossible detail + reason to watch to end
- Every line moves toward payoff. Cut filler.
- Cause-and-effect: but / so chaining between beats
- False calm beat before final scare
- Payoff = jumpscare cue, then STOP (no doom linger)
- If subscribe CTA: BEFORE payoff, never only after

VISUALS (Jenny 05):
- 3-10 mute-safe beats — horror shots acting the wrong detail
- Subtitles on screen for key lines (spoken_text per segment)
- Framing: subject in upper 60%; captions above YouTube Shorts title overlay
- Review on mute before upload — story must read without audio
"""

# Legacy alias — cosy rules kept for course tooling only.
JENNY_SCRIPT_RULES = HORROR_SCRIPT_RULES


def check_jenny_voice(script: str, hook: str) -> list[str]:
    """Runtime lint for Don't Blink horror scripts (second-person immersive)."""
    issues: list[str] = []
    combined = f"{hook}\n{script}"
    if not _SECOND_PERSON.search(combined):
        issues.append("Missing second-person voice — horror Shorts put the viewer in the scene (you/your).")
    if re.search(r"\b(hey guys|everyone|people|folks)\b", combined, re.I):
        issues.append("Plural audience — use singular 'you'.")
    if script.lower().startswith(("in this video", "today we", "let's talk about", "welcome back")):
        issues.append("Weak opener — start the video ASAP with the impossible hook.")
    if re.search(r"\b(scary story\s*#?\d+|episode\s*\d+)\b", combined, re.I):
        issues.append("Series numbering — launch week hooks must be standalone impossible details.")
    if "subscribe" in script.lower() and script.lower().rfind("subscribe") > len(script) * 0.85:
        issues.append("CTA may be after payoff — move subscribe ask before resolution.")
    return issues
