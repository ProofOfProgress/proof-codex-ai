# PERIPHERAL — industrial death-metal aesthetic (YouTube-safe)

**Vibe:** Slipknot-adjacent **theatre** — masks, jumpsuits, warehouse pit, red strobe, chains. Not a documentary of harm.

**Merch crossover:** same eye mark + **PERIPH** patches on black denim / jumpsuit cuts — label energy, not cosplay only.

---

## What “bird head” means on this channel (symbol, not snuff)

| OK (show) | Never show (18+ / strike risk) |
|-----------|--------------------------------|
| Porcelain or metal **beak mask** on a hooded figure | Live bird, real animal, chewing, biting flesh |
| **Feathers** on mask collar, stage floor, ritual plate | Eating / consuming animal on camera |
| Empty **cage**, open gate, feathers scattered | Blood spray, open wounds, step-by-step harm |
| Masked figure **holds mask** with beak shape — camera cuts before mouth | Graphic gore, torture, real victims |
| Off-screen **crunch** → cut to aftermath (empty stage, red light, one feather falling) | Animal cruelty depiction |

The horror is **theatre and implication** — audience fills the gap. Same rule as implied gore everywhere on PERIPHERAL.

---

## Visual grammar

- **Masks:** numbered metal plates, stitched lips, hollow eye holes — never a real celebrity likeness
- **Wardrobe:** black industrial jumpsuit, chain harness, biker leather layer (merch path)
- **Set:** concrete warehouse, fog, single red strobe, chain hanging from ceiling, mosh-pit empty circle
- **Palette:** black, bone white, cold steel, **red strobe accent only** — not blood spray
- **Eye brand:** macro freaky eye on mask forehead or final beat iris fill — when earned
- **Motion:** slow head-tilt / chain sway → false calm → snap lunge from edge of frame

---

## Audio (programmatic — no copyrighted tracks)

- Low **chug** under VO (ffmpeg lavfi)
- **Blast-beat** hit on scare line
- Distorted whisper or growl **one syllable max** under mask — not full song

See `shorts_bot/production/horror_sfx_mix.py` — `metal_chug`, `metal_hit` cues.

---

## YouTube / YPP (stay monetizable, not 18+)

- **No animal cruelty** — feathers and masks only
- **No explicit gore** — anticipation + aftermath
- **No real religion attacks** — fictional industrial cult **performance**, not mocking faiths
- **Volume warning** on finale-scare uploads
- **Synthetic media** disclosed on upload

If a script or visual beat crosses the line, `metal_aesthetic.py` + `ypp_bans.py` should block before render.

---

## Code

`shorts_bot/production/metal_aesthetic.py` — injected into scripts, I2V prompts, QC context.
