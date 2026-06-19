"""Niche — Peripheral (analog/CCTV horror Shorts)."""

from __future__ import annotations

from shorts_bot.production.world import WORLD_NAME, world_rules_compact

NICHE_NAME = "Peripheral"
NICHE_TAGLINE = "Watch the whole thing."

NICHE_POSITIONING = f"""
Peripheral — **analog/CCTV nightmare Shorts** (~30 seconds) from **{WORLD_NAME}**.
Fullscreen security footage catches what reality hides. Old villagers still **worship the Eye** in background lore.
Second-person ownership hooks. Subtitles when dialogue exists. AI cinematic video (Sora-class when available).

{world_rules_compact()}

Episode pillars (rotate):
1. **Motion alert** — CCTV flags an empty room before the scare appears
2. **Recording lag** — playback shows a different timeline
3. **Mirror/feed mismatch** — reflection or mask moves one beat late
4. **3:12 AM rule** — alarm clock/REC timestamp anchors the wrongness
5. **Eye leak** — village/Eye lore bleeds into the analog feed

Format rules:
- Second-person ownership hook — "Your security camera..." / "You live alone..."
- Hook in line 1 = **premise** (broken rule — not vague mood)
- Victims notice recordings before reality catches up
- Twist rewrites hook — full-frame Eye or uncanny lunge — then STOP
- 25–35s; subtitles burned in post

What works: security cam ownership, empty-room motion, clear 3:12 AM clock, final lunge/sting, heavy SFX.
What fails: phone screens, faceless narrator, repeated glitch-hour filler, template farms, cosy tone.
"""

DEFAULT_TOPICS = [
    "your security camera flagged motion at 3:12 AM — you live alone",
    "your hallway camera replayed tomorrow's footsteps",
    "your alarm clock hit 3:12 AM before the room went quiet",
    "your mirror feed blinked one second after you did",
    "your doorbell camera recorded someone leaving your apartment from inside",
    "your baby monitor whispered your name from an empty room",
    "your night-vision camera found eyes behind the closed closet door",
    "your kitchen camera showed a chair turn toward the hallway",
    "your locked apartment camera showed the deadbolt turning from inside",
    "your bedroom camera replayed you sleeping with your eyes open",
    "your elevator camera stopped at a floor your building does not have",
    "your stairwell camera counted one extra shadow behind you",
    "your living-room feed froze except for the thing under the table",
    "your webcam light turned on while the laptop was unplugged",
    "your hallway motion box followed something standing perfectly still",
    "your apartment feed showed the old village symbol on your door",
    "your mirror reflected the Eye before the glass went black",
    "your security playback showed you kneeling to the Eye",
    "your nightstand clock flashed 3:12 AM in every room at once",
    "your final camera frame was taken from behind your own eyes",
]


def quality_lessons() -> str:
    return (
        "Better: second-person owned security-camera hook, fullscreen CCTV, clear 3:12 AM anchor, "
        "empty-room motion before reality catches up, subtitles on dialogue, heavy SFX, twist sting. "
        "Worse: phone screens, faceless narrator, repeated glitch-hour filler, template farms, cosy tone. "
        "Always: 🔊 volume warning when stinging, declare synthetic media, rotate scare pillars."
    )
