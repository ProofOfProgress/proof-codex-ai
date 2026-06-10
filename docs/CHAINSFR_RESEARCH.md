# ChainsFR + stick-figure Short research

Deep reference for Soft Continuity video format. **We do not use Claude/Higgsfield** — this repo renders locally with TurboScribe timestamps + PIL stick frames.

## ChainsFR (primary reference)

| Trait | Detail |
|-------|--------|
| Format | Voice-over story + stick figures **acting** each beat |
| Style | Minimal MS-Paint line art, expressive poses, speech bubbles for dialogue |
| Backgrounds | **Change per beat** — rooms, doors, outdoors — simple props literal to script |
| Retention | Story clarity on mute; visual matches spoken line exactly |
| Scale | ~4M+ subs, relatable “first time / be like” storytime Shorts |

Sources: [ChainsFR Wiki](https://chainsfr.fandom.com/wiki/ChainsFR_Wiki), [YouTube Fandom](https://youtube.fandom.com/wiki/ChainsFR), [Bloop Animation overview](https://www.bloopanimation.com/6-stick-figure-animators-you-should-know/).

## Zen-style case study (your transcript)

Faceless channel reposting simple drawings with explosive growth. Mechanics that matter:

1. **One image per TurboScribe timestamp** — not one image per paragraph
2. **Cut every 2–3 seconds** — retention from visual velocity, not polish
3. **MS-Paint aesthetic** — white/off-white, beginner drawing, black outlines
4. **Voice clone / real VO** + TurboScribe for sync (we use Resemble + Whale)
5. **Automation** = timestamped script → batch stills → timeline by filename (`00.07.png` → 7s)

We match (3)(4)(5) in `finish_draft_pipeline`; we use **ChainsFR storytelling** instead of primitive-human niche.

## Soft Continuity twist: **same couch**

User requirement: background **varies**, but **couch stays identical** every frame (sitcom anchor).

| Layer | Rule |
|-------|------|
| Back | Wall, window (night/morning/rain/Sunday grey), door, lamp, plant, calendar |
| Mid | **Fixed couch** — same position, color, arm rests |
| Front | Stick figure on/near couch acting the line |
| Props | Phone, laptop, clock — literal to script |
| Captions | ffmpeg ASS safe zone — not baked narration text |

Implementation: `shorts_bot/production/stick_background.py`, `render_stickfigures.py`.

## Background mapping (auto)

| Script cue | Background |
|------------|------------|
| 3am, night, phone | Night window + moon + dim lamp |
| Sunday, email, work | Grey window + wall calendar |
| breathe, calm, still here | Warm floor lamp + plant |
| conversation, text, angry | Door + side phone table |
| party, walk in alone | Dark window + entry door |
| presentation, interview | Desk corner + papers |

## Pipeline (this repo)

```
Gemini script → Resemble VO → TurboScribe timestamps → stick frames (couch + bg) → ffmpeg → upload
```

Config: `VISUAL_STYLE=stickfigure` (default).

## Anti-patterns

- AI cinematic stills (unless user overrides `VISUAL_STYLE=ai`)
- One background for whole video
- Narration text drawn on frames (use captions)
- Sparse cuts (>4s per still on a 60s Short)
