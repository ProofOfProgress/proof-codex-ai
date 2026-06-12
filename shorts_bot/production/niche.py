"""Niche — Peripheral (faceless horror Shorts, end jumpscare)."""

from __future__ import annotations

from shorts_bot.production.world import WORLD_NAME, world_rules_compact

NICHE_NAME = "Peripheral"
NICHE_TAGLINE = "Watch the whole thing."

NICHE_POSITIONING = f"""
Peripheral — **faceless horror Shorts** (~30 seconds). Each upload = **one Black Mirror episode** compressed: premise → escalation → twist → sting.
Anthology — rotate settings ({WORLD_NAME} apartment, village curse-sign, warehouse pit); same episode grammar, different mask.
AI full-motion clips only (no stick figures). Eyes, hallways, CCTV, masks — never cosy self-help.
Merch tagline: *don't blink* — not the channel name.

{world_rules_compact()}

Episode pillars (rotate):
1. **Wrong place** — empty room, locked door, hallway that wasn't there yesterday
2. **Wrong time** — timestamp glitch, photo taken after death, 3am notification
3. **Wrong reflection** — mirror, window, phone screen shows someone else
4. **Wrong sound** — knock when alone, breathing on a muted call, footsteps upstairs
5. **Wrong text** — last message from a deleted contact, autocorrect to something impossible

Format rules:
- Hook in line 1 = **premise** (broken rule — not vague mood)
- 6–8 beats, cut every 2–3s, visual change each beat; consequences escalate
- Beat 6–7: false calm (quiet VO) — bait the swipe
- Twist line rewrites the hook — then full-frame sting + audio (🔊 volume warning)
- 25–35s total length — not 60s slow burn; **no explanation after the sting**

What works: Black Mirror "what-if", twist that recontextualizes hook, earned sting, village/apartment/pit rotation.
What fails: random noise scares, generic creepypasta listicles, gore, real victims, cosy aesthetic, stick figures.
"""

DEFAULT_TOPICS = [
    "the last text showed delivered — but their phone was off",
    "you took a photo of your room — someone was in the corner",
    "the knock came from inside the closet you never open",
    "your security camera flagged motion — you live alone",
    "the mirror reflection blinked one second after you did",
    "voicemail from your own number — timestamp tomorrow",
    "the hallway was three steps longer than yesterday",
    "every light in the house turned on — you didn't touch a switch",
    "the baby monitor picked up a second heartbeat",
    "your face unlock worked — but you weren't looking at the phone",
    "the GPS says you're home — the camera shows an empty driveway",
    "you muted the call — the breathing didn't stop",
    "the door was locked from the inside — the key is still in your pocket",
    "the photo timestamp is from next week",
    "something sat on the edge of your bed — the sheets are still cold",
    "the elevator stopped on a floor that doesn't exist",
    "your smart speaker answered a question you didn't ask",
    "the scratch marks on the door are on the inside",
    "you woke up with sand in your bed — you don't live near a beach",
    "the figure in the window waved before you looked up",
    "the lullaby played from the empty nursery",
    "your reflection didn't put the phone down when you did",
    "the emergency alert was for your exact address — wrong date",
    "you heard your voice calling from the basement",
    "the family photo has one more person than you remember",
    "the scarecrow faces your window every morning — closer than yesterday",
    "the static on the TV formed a face for one frame",
    "you found a second set of teeth marks on the apple",
    "the car headlights behind you never passed — for twenty miles",
    "don't blink at the end — the thing in the hall moves when you do",
    # Industrial metal theatre — symbolic bird/offering (YPP-safe topics)
    "segment seven left feathers on the pit floor — the cage was empty",
    "the beak mask was warm — you never took it off",
    "the warehouse circle had one extra jumpsuit — your size",
    "the blast beat dropped — every mask turned to you",
    "the offering plate held feathers only — something crunched off-screen",
    "mask number three was missing — yours was already on",
    "the red strobe caught chain sway — the pit had no audience",
    "they chant one syllable under the mask — then silence",
    "the PERIPH patch on your jacket wasn't yours — it was stitched inside out",
    # Village curse-sign thread (Black Mirror rule horror — YPP-safe implied sickness)
    "the village sign showed your name — everyone else looked away",
    "you saw the thing on the barn door — by morning you couldn't keep water down",
    "grandma said never stare at the signpost — you counted three seconds too long",
    "the fog lifted and the square was empty — except the symbol only you could see",
    "every villager brought you soup — none of them would meet your eyes",
    "the doctor said your stomach was fine — you hadn't eaten in nine days",
    "you filmed the sign to prove it wasn't real — the playback showed you already watching",
]


def quality_lessons() -> str:
    return (
        "Better: strong wrong-detail hook in line 1, 6–8 paced beats, false calm before scare, "
        "AI motion clips synced to VO, jumpscare on final beat with audio sting. "
        "Worse: generic 'scary story', cosy self-help tone, stick figures, 60s slow build, "
        "same scare every upload. Always: 🔊 volume warning, captions in Jenny 05 safe zone, "
        "declare synthetic media, rotate scare types."
    )
