"""ChainsFR + high-velocity stick Short research (no Claude/Higgsfield required)."""

from __future__ import annotations

CHAINSFR_VISUAL_BRIEF = """
STICK FIGURE FORMAT (ChainsFR-inspired — Soft Continuity / The Minute Before):

REFERENCE CREATORS:
- **ChainsFR** (~4M subs): voice-over story + stick figures ACTING each beat. Simple rooms,
  speech bubbles for dialogue, props for literal script moments. Background CHANGES per beat;
  characters stay in a recognizable space.
- **Zen-style faceless explosion** (case study): one still per TurboScribe timestamp, cuts every
  2–3 seconds, MS-Paint-simple drawings on white/off-white. Retention = frequency of visual change
  synced to voice, not cinematic quality.

SOFT CONTINUITY RULE (your twist):
- **Same couch every frame** — anchor continuity like a sitcom set.
- **Background rotates** behind the couch: window (night/morning/rain), door, lamp, plant, calendar,
  side desk — matched to the script line.
- Stick figure on/near couch acts out the protocol; speech bubbles only for quoted dialogue.
- Captions in Jenny 05 safe zone (ffmpeg ASS), not narration text baked into frames.

PIPELINE (this repo — not Claude):
Gemini script → Resemble voice → TurboScribe timestamps → local stick render → ffmpeg.

CUT DENSITY: target 2–3s per frame when TurboScribe available; script fallback uses ~2.5s segments.
"""


def chainsfr_research_block() -> str:
    return CHAINSFR_VISUAL_BRIEF.strip()
