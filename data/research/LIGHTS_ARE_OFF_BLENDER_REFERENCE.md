# LIGHTS ARE OFF — Blender quality bar (owner reference)

**North star:** Peripheral horror Shorts should look **finished in Blender** like this channel — not grey block-outs, not broken textures, not “viewport test.”

**Tool stack match:** 100% Blender EEVEE on cloud. No Kling for hero scenes. Creature motion = Mixamo/Uthana → FBX.

---

## Reference videos (show these to Gemini + every visual QC prompt)

| Video | URL | Length | What to steal |
|-------|-----|--------|---------------|
| **Swim here** (viral Short) | https://youtube.com/shorts/R7cEIG_gqLU | ~15s | Hook frame reads in 1s; environment + dread; payoff timing |
| **I Made a Self-Aware Robot** (Pt 1) | https://youtu.be/S0x2llxEAjk | ~8 min | Lab set dressing; materials; 3-point lighting; character + world |
| **Held Prisoner by Robot** (Pt 3) | https://youtu.be/lnDP902qeqw | ~10 min | Asset reuse; escalation; readable workshop; cinematic framing |
| **Channel** | https://www.youtube.com/@LIGHTSAREOFF | — | Series craft; “no AI” Blender animation; horror that feels **real** |

Creator note on long videos: *“No AI was used at all in the making of this video. This animation was made entirely in Blender.”*

---

## What “good” means (fail if missing)

1. **Environment reads instantly** — viewer knows it’s a gas station / road / fog in under 1 second  
2. **Textures work** — no magenta, no flat grey untextured blocks (FBX paths must relink to `Textures/`)  
3. **Horror lighting** — key + fill + rim; streetlight flicker motivates the scare (Grant Abbitt / Blender Guru EEVEE)  
4. **Camera is intentional** — POV walk, push-in, dutch tilt; not random default cube viewport  
5. **Creature in the world** — Form 2 lit by the same lights as the set, grounded on asphalt  
6. **Preview frame approval** — owner sees one still that looks like LIGHTS ARE OFF **before** YouTube schedule  

---

## What we failed on draft #2 (2026-06-14)

- Gas station FBX imported but **Windows texture paths broke** → scene looked unchanged / unfinished  
- Night grade crushed albedo → black void  
- Procedural fallback cubes still “won” visually when env failed  

**Fix order:** relink textures → re-light → re-frame camera → vision QC with this doc → re-render → then upload.

---

## Free courses agents must complete (Blender videogen)

| Course | URL | Module |
|--------|-----|--------|
| Blender Guru — EEVEE | https://www.youtube.com/watch?v=-gW6vk_OuNQ | EEVEE render settings |
| Blender Guru — Lighting | https://www.youtube.com/watch?v=Ys4793edotw | Night exteriors |
| Grant Abbitt — Horror lighting | https://www.youtube.com/watch?v=Ys4793edotw (search “Horror Made Easy”) | 3-point + shadows |
| Official bpy quickstart | https://docs.blender.org/api/current/info_quickstart.html | Headless pipeline |

Drills: `python3 -m shorts_bot.production.blender.bpy_lab`

---

## Peripheral application (gas station Form 2)

- **Clip 1 (0–10s):** POV toward pumps; flicker reveals too-tall figure at tree line  
- **Clip 2 (10–20s):** Uncanny wave between pumps; environment visible (canopy, signs, wet asphalt)  
- **Clip 3 (20–30s):** Lunge; face fills frame; emissive pump signs still readable in background  

Silent launch — SFX only, no dialogue. Match LIGHTS ARE OFF **craft**, not their robot vlog format.
