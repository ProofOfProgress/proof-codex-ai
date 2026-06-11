# Channel identity — Don't Blink

> **Terrifying faceless horror Shorts** — ~30s micro-stories, **jumpscare at the end**.

## One-line pitch

**Faceless horror Shorts that hit you in the last 3 seconds — if you blink, you miss it.**

## World (The Gap)

Every Short is **another night in the same universe** — not a random scare swap.

- **Law:** reality and recordings are **one beat out of sync**; things move when you blink, look away, or refresh the feed
- **Time:** **3:12 AM** on the alarm clock — when cams and timestamps glitch widest
- **Place:** same liminal alone-at-night apartment grammar (hallway, mirror, alarm clock, security cam, closet)
- **Threat:** faceless in lag/peripherals until the final lunge — never named in VO

Full bible: `channel/brand/world.md` — injected into scripts and I2V prompts via `shorts_bot/production/world.py`.

**Horror lane (locked):** **Analog horror** + psychological — see `channel/brand/horror_lane.md`.

## Niche

| Old (Soft Continuity) | New (Don't Blink) |
|-----------------------|-------------------|
| Cosy self-help protocols | Impossible-detail horror micro-stories |
| Stick figures on couch | AI full-motion cinematic clips |
| 60s calm payoff | 25–35s → **jumpscare payoff** |
| "you're still here. good." | "Watch the whole thing." |

**Handle:** `@alphabeta0-c1m` (unchanged)  
**Display name target:** Don't Blink  
**YouTube note:** Display name **cannot** be changed via YouTube Data API (Google returns `channelTitleUpdateForbidden` — API silently keeps the old title). Description + banner update via API; **name must be set in YouTube Studio** (Customization → Basic info). Studio previously rejected **"Don't Blink"** as taken/unavailable. Alternates: **Never Blink**, **Dont Look Away**, **Don't Blink Shorts**. You can change the name **twice per 14 days**.

## Tone

| Do | Don't |
|----|-------|
| Specific uncanny hooks (timestamp, reflection, text) | Generic "scary story #47" |
| Earned scare — setup → silence → hit | Random loud noise with no story |
| Rotate scare types each upload | Same monster every video |
| 🔊 Volume warning in description/title | Surprise-report bait |
| Faceless — shadows, eyes, hallways, CCTV | Gore, real victims, child harm |

## Visual system

- **Format:** `VISUAL_STYLE=ai_video` — FLUX still → I2V motion per beat
- **Palette:** black, cold blue, deep crimson, film grain, harsh contrast
- **No stick figures**
- **Final beat:** full-frame lunge / face / glitch — synced audio sting
- **Captions:** ffmpeg ASS, Jenny 05 safe zone

## Growth

- Series recognition: viewers learn **the scare is always at the end**
- Binge: "one more" loop — completion rate matters more than RPM
- Comments: "I jumped" / "volume warning" = engagement signal

## Brand assets

- **Profile:** circle crop from center of banner eye (iris)
- **Banner:** macro terrifying eye, 2560×1440, no text (eye is the logo)
