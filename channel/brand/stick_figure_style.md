# Stick figure style — ChainsFR-inspired (Soft Continuity)

**Default video format** for *The Minute Before* Shorts. See `docs/CHAINSFR_RESEARCH.md` for full research.

## Core rule: act the beat, minimal set

- **Character** — black stick figure **acting** the spoken line (pose changes every timestamp)
- **Background** — changes per beat; plain off-white when nothing specific is needed
- **Furniture** — bed for sleep/3am beats; couch only when script says sit/couch
- **Props** — only what the line mentions (phone, door, clock)
- **Cuts** — one still per TurboScribe timestamp (~every 2–3 seconds)

## Visual rules (9:16) — cosy

- **Canvas:** warm cream `#F5EFE6`, floor `#E8DFD4`, MS-Paint-simple `#1A1A1A` outlines
- **Sets:** lamp glow, rainy window, couch + throw, bed, mug — see `cosy_aesthetic.md`
- **Characters:** round head, expressive poses (ChainsFR)
- **Speech bubbles:** quoted dialogue only — narrator lines use captions (ffmpeg ASS)
- **Jenny 05:** action in upper 60%; bottom ~320px clear for Shorts UI
- **Default mood:** warm domestic quiet — avoid office desk / bathroom stall unless script says so

## Pose per beat

Each timestamp = one scene: character **doing** what the voice says — standing at a door, breathing, putting phone down, lying awake, etc.

## Anti-slop

- Every scene must match the spoken line literally
- Do not repeat the same couch/room layout every frame
- No photorealism, no 3D, no dark void circles
