"""ChainsFR + high-velocity stick Short research (no Claude/Higgsfield required)."""

from __future__ import annotations

CHAINSFR_VISUAL_BRIEF = """
STICK FIGURE FORMAT (ChainsFR — Soft Continuity / The Minute Before):

REFERENCE: **ChainsFR** (~4M subs)
- Voice-over story + stick figures **acting** each beat (not frozen lecture poses)
- MS-Paint-simple line art, black outlines, off-white backgrounds
- **Background changes per beat** — bedroom, doorway, hallway, outdoors — only what the line needs
- **Character is NOT locked to one couch** — they stand, walk, sit on bed, lean at a door, etc.
- Speech bubbles **only** for quoted dialogue; narrator lines use captions (ffmpeg ASS)
- Props are **literal and minimal** — phone when texting, door when walking in, clock when it's 3am
- Retention = visual change every 2–3s synced to voice, not cinematic polish

ZEN-STYLE CASE STUDY (velocity):
- One still per TurboScribe timestamp
- Cut every 2–3 seconds
- If a beat doesn't need a window, plant, and couch — **don't draw them**

PIPELINE (this repo):
Gemini script → Resemble voice → TurboScribe timestamps → local stick render → ffmpeg.

CUT DENSITY: target 2–3s per frame; script fallback ~2.5s segments.
"""


def chainsfr_research_block() -> str:
    return CHAINSFR_VISUAL_BRIEF.strip()
