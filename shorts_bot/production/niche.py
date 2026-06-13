"""Niche — Peripheral (village Eye worship horror Shorts)."""

from __future__ import annotations

from shorts_bot.production.world import WORLD_NAME, world_rules_compact

NICHE_NAME = "Peripheral"
NICHE_TAGLINE = "Watch the whole thing."

NICHE_POSITIONING = f"""
Peripheral — **first-person nightmare Shorts** (~30 seconds) from **{WORLD_NAME}**.
Villagers **worship the Eye**. The Eye tortures you in dreams; you remember when you wake.
Character voices on screen only — no narrator. Subtitles always. AI cinematic video (Sora-class when available).

{world_rules_compact()}

Episode pillars (rotate):
1. **Worship exposed** — you witness the ritual; villagers know you saw
2. **Dream invasion** — Eye true form in sleep; waking residue
3. **Wrong villager** — uncanny human, rabies-wrong, shape-shifting energy
4. **Outsider rule** — name on sign, symbol on barn, soup with averted eyes
5. **Perception break** — reality fractures after the Eye touches you

Format rules:
- First person **I** — screenplay dialogue, no off-screen narrator
- Hook in line 1 = **premise** (broken rule — not vague mood)
- Victims **remember dreams** on waking Shorts
- Twist rewrites hook — full-frame Eye or uncanny lunge — then STOP
- 25–35s; subtitles burned in post

What works: Eye lore binge, village complicity, dream true form, uncanny humans, heavy SFX.
What fails: CCTV apartment spam, faceless narrator, glitch hour hooks, template farms, cosy tone.
"""

DEFAULT_TOPICS = [
    "the village sign showed my name — everyone else looked away",
    "I saw them praying to the Eye in the barn — they know I watched",
    "I woke up tasting metal — I remembered the Eye",
    "the villager smiled with too many teeth — then spoke in my mother's voice",
    "they brought me soup — none of them would look at my face",
    "I dreamed the Eye filled the ceiling — I was still screaming when I woke",
    "grandma said never stare at the signpost — I counted four seconds too long",
    "every candle in the square pointed at me — I was the only outsider",
    "the doctor said I was fine — I hadn't slept in six days",
    "I filmed the ritual to prove I was sane — the playback showed me kneeling",
    "the fog lifted and the symbol on the barn was my initials",
    "I asked who they worship — the whole square went silent",
    "my neighbor's eyes were wrong — both pupils too wide, never blinking",
    "I heard them chanting one word under their breath — it wasn't a language",
    "the child in the window pointed at the sky — there was nothing there until I looked",
    "I tried to leave the village — the road was the same square again",
    "they left a white hooded robe on my doorstep — it fit",
    "I dreamed they cut out my tongue — I woke up unable to speak for an hour",
    "the priestess of the Eye smiled — she had my face",
    "I blinked and every villager was staring at the same spot behind me",
]


def quality_lessons() -> str:
    return (
        "Better: first-person I, Eye worship or dream invasion hook, uncanny villager visible, "
        "victims remember dreams, subtitles on all dialogue, heavy SFX, twist sting. "
        "Worse: CCTV apartment spam, faceless narrator, glitch hour, template farms, cosy tone. "
        "Always: 🔊 volume warning when stinging, declare synthetic media, rotate scare pillars."
    )
