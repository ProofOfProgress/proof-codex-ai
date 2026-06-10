# ChainsFR + stick-figure Short research

Deep reference for Soft Continuity video format. **We do not use Claude/Higgsfield** — this repo renders locally with TurboScribe timestamps + PIL stick frames.

## ChainsFR (primary reference)

| Trait | Detail |
|-------|--------|
| Format | Voice-over story + stick figures **acting** each beat |
| Style | Minimal MS-Paint line art, expressive poses, speech bubbles for dialogue |
| Backgrounds | **Change per beat** — bedroom, doorway, outdoors — **only what the line needs** |
| Character | **Not locked to one couch** — stands, walks in, sits on bed, leans at door |
| Props | Literal to script (phone, door, clock) — **no filler plant/clock every frame** |
| Retention | Story clarity on mute; visual matches spoken line exactly |
| Scale | ~4M+ subs, relatable “first time / be like” storytime Shorts |

Sources: [ChainsFR Wiki](https://chainsfr.fandom.com/wiki/ChainsFR_Wiki), [YouTube Fandom](https://youtube.fandom.com/wiki/ChainsFR), [Bloop Animation overview](https://www.bloopanimation.com/6-stick-figure-animators-you-should-know/).

## Zen-style case study (velocity)

Faceless channel reposting simple drawings with explosive growth. Mechanics that matter:

1. **One image per TurboScribe timestamp** — not one image per paragraph
2. **Cut every 2–3 seconds** — retention from visual velocity, not polish
3. **MS-Paint aesthetic** — white/off-white, beginner drawing, black outlines
4. **Voice clone / real VO** + TurboScribe for sync (we use Resemble + Whale)
5. **Automation** = timestamped script → batch stills → timeline by filename (`00.07.png` → 7s)

## Soft Continuity rules (learned from ChainsFR)

| Layer | Rule |
|-------|------|
| Background | Plain wall unless the line needs night window, door, desk, etc. |
| Furniture | Bed for sleep beats; couch **only if script says sit/couch** |
| Character | Black stick figure **acting** the line — pose changes every beat |
| Props | One literal prop max when the line mentions it |
| Captions | ffmpeg ASS safe zone — not narration text baked into frames |

Implementation: `shorts_bot/production/stick_background.py`, `render_stickfigures.py`, `scene_plan.py`.

## Background mapping (auto, minimal)

| Script cue | Draw only |
|------------|-----------|
| 3am, night | Night window (+ moon) |
| Sunday, work email | Grey window (+ calendar if Sunday/Monday) |
| breathe, calm | Warm lamp |
| angry text, door | Door |
| party, walk in alone | Dark window + door |
| presentation | Desk corner |
| generic beat | Plain off-white + figure |

## Pipeline (this repo)

```
Gemini script → Resemble VO → TurboScribe timestamps → stick frames (minimal scenes) → ffmpeg → upload
```

Config: `VISUAL_STYLE=stickfigure` (default).

## Anti-patterns

- **Same couch every frame** (sitcom lock-in — not ChainsFR)
- Decorative plant + clock on every beat when script doesn't mention them
- AI cinematic stills (unless user overrides `VISUAL_STYLE=ai`)
- One background for whole video
- Narration text drawn on frames (use captions)
- Sparse cuts (>4s per still on a 60s Short)
