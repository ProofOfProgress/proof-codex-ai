# Stick figure style — ChainsFR-inspired (Soft Continuity)

**Default video format** for *The Minute Before* Shorts. See `docs/CHAINSFR_RESEARCH.md` for full research.

## Core rule: same couch, changing room

- **Couch** — identical every frame (position, color, shape). Sitcom anchor.
- **Background** — rotates per timestamp: window (night/morning/rain), door, lamp, plant, calendar, desk.
- **Character** — black stick figure on/near couch, **acting** the spoken line.
- **Cuts** — one still per TurboScribe timestamp (~every 2–3 seconds).

## Visual rules (9:16)

- **Room wall:** warm off-white `#E8E5DE`, MS-Paint-simple outlines
- **Couch:** `#C4B8A8` with dark outline — never move or resize between frames
- **Characters:** black stick figures, round head, expressive poses (ChainsFR)
- **Speech bubbles:** quoted dialogue only — narrator lines use captions (ffmpeg ASS)
- **Props:** phone, laptop, clock, door — literal to script line

## Pose per beat

Each timestamp = one scene: character **doing** the protocol on the couch (or standing by couch for “walk in / try this” beats).

## Jenny 05

Action in upper 60%; bottom ~320px clear for Shorts UI + burned captions.

## Anti-slop

- Every scene must match the spoken line literally
- Vary background props — not the couch
- No photorealism, no 3D, no dark void circles (channel banner uses dark palette; **video frames stay bright room**)
