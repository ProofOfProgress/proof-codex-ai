# Channel identity — Peripheral

> **Faceless horror Shorts** (~30s) — jumpscare at the end. **Brand:** Peripheral · **Tagline on merch:** don't blink

## One-line pitch

**Horror for the corner of your eye — watch the whole thing.**

## Logo & merch

| Element | Spec |
|---------|------|
| **Brand name** | **PERIPHERAL** (display: Peripheral) |
| **Merch shorthand** | **PERIPH** |
| **Mark** | Single eye, white hairline on black, staring straight at the viewer — hollow or centered pupil, no face |
| **Hero print** | Huge eye on back; small lowercase **don't blink** underneath |
| **Front** | Minimal — small PERIPH crest or blank |
| **Tagline** | *don't blink* is **merch/copy only**, not the YouTube channel name |

## World (optional texture — not the brand name)

Stories can share mood (alone at night, uncanny domestic wrongness) without one plot template. See `channel/brand/world.md` for optional continuity (`The Gap`).

**Horror lane (locked):** **Analog horror** + psychological — `channel/brand/horror_lane.md`.

## Niche

| Avoid | Peripheral |
|-------|------------|
| Cosy self-help | Impossible-detail horror micro-stories |
| Stick figures | AI full-motion cinematic clips |
| Same scare gimmick every title | Anthology — watched / stalked / peripheral dread |
| Generic "scary story #47" | Specific hooks (reflection, cam, knock, text, timestamp) |

**Handle:** `@alphabeta0-c1m` (unchanged until rebrand)  
**Display name:** **Peripheral** (set in YouTube Studio — API cannot change channel title)  
**Studio note:** You can rename **twice per 14 days**.

**Channel description (source of truth):** `channel/brand/youtube_copy.txt` — first line is the homepage preview before "Show more". Apply: `python3 -m shorts_bot.youtube.brand_cli`. Audience delivery research: `data/research/PERIPHERAL_AUDIENCE_DELIVERY_RESEARCH.md`.

## Tone

| Do | Don't |
|----|-------|
| Specific uncanny hooks | Generic creepypasta listicles |
| Earned scare — setup → silence → hit | Random loud noise |
| Rotate scare pillars | Same monster every video |
| 🔊 Volume warning on finale-scare drafts | Surprise-report bait |
| Faceless — shadows, eyes, hallways, CCTV | Gore, real victims, child harm |

## Visual system

- **Format:** `VISUAL_STYLE=ai_video` — I2V motion per beat when generation enabled
- **Palette:** black, cold blue, deep crimson, film grain, harsh contrast
- **Logo on channel:** line eye (profile crop from iris)
- **Final beat:** full-frame lunge — synced audio sting when finale profile
- **Captions:** ffmpeg ASS, safe zone above Shorts UI

## Growth

- Brand recognition: **Peripheral** + staring eye; **don't blink** on merch/descriptions
- Binge: completion rate > RPM
- Comments: "I jumped" / volume warning = engagement signal

## Brand assets

- **Profile:** center crop of line eye mark
- **Banner:** macro eye, white on black, no channel name text (eye is the logo)
