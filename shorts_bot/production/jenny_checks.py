"""Jenny Hoyos course constraints for faceless personal Shorts."""

from __future__ import annotations

import re

from shorts_bot.course.loader import CourseKnowledgeBase
from shorts_bot.config import settings


_FIRST_PERSON = re.compile(
    r"\b(i|i'm|i've|i'd|my|me|same here|i used to|honestly|look)\b",
    re.I,
)


def jenny_draft_guidance(topic: str) -> str:
    from shorts_bot.course.router import CourseRouter

    kb = CourseKnowledgeBase(settings.course_dir)
    r = CourseRouter(kb)
    guidance = r.build_guidance(
        f"faceless short personal storyteller struggles what helped me "
        f"idea hook visual mute retention payoff relatability singular you {topic}"
    )
    return f"JENNY COURSE (enforce hook→momentum→payoff, mute-safe visuals, singular you):\n{guidance}\n"


JENNY_SCRIPT_RULES = """
VOICE — real faceless creator (Jenny 07 + 09):
- First person: "I", "my", "I used to…", "this helped me"
- Same struggles as viewer — not guru on a pedestal
- Singular "you" — one person talking to one person
- Share what actually helped YOU, not lecture mode

STRUCTURE (Jenny 02 + 06):
- Hook = shock/curiosity + reason to stay to the end. Start IMMEDIATELY.
- Every line moves toward payoff. Cut filler.
- Cause-and-effect: but / so chaining between beats
- Payoff = best beat, then STOP (no doom linger)
- If subscribe CTA: BEFORE payoff, never only after

VISUALS (Jenny 05):
- 3-5 mute-safe beats — stick figures ACTING the advice (ChainsFR-style, off-white frames)
- Subtitles on screen for key lines (spoken_text per segment)
- Framing: subject in upper 60%; captions above YouTube Shorts title overlay (safe zone)
- Review on mute before upload — story must read without audio

ANTI-SLOP (verbatim):
- No forced relatability, no trend copy-paste, no generic motivation spam
"""


def check_jenny_voice(script: str, hook: str) -> list[str]:
    issues: list[str] = []
    if not _FIRST_PERSON.search(script) and not _FIRST_PERSON.search(hook):
        issues.append("Missing first-person voice — sound like a creator sharing their struggle.")
    if re.search(r"\b(hey guys|everyone|people|folks)\b", script, re.I):
        issues.append("Plural audience — Jenny wants singular 'you'.")
    if script.lower().startswith(("in this video", "today we", "let's talk about")):
        issues.append("Weak opener — Jenny: start the video ASAP.")
    if "subscribe" in script.lower() and script.lower().rfind("subscribe") > len(script) * 0.85:
        issues.append("CTA may be after payoff — move subscribe ask before resolution (file 09).")
    return issues
