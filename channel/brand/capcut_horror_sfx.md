# CapCut — Don't Blink horror SFX workflow

**Read first:** `data/research/HORROR_SOUND_EFFECTS_RESEARCH.md` (why each SFX type works).

## Project defaults

- Ratio **9:16** · 25–35s · **30 fps**
- Import from production pack: `voiceover.mp3`, clips from `clips/` (or `images/`), `captions.srt` optional
- **Three audio tracks:** VO (top priority) → SFX → Music/ambience (lowest)

---

## Step-by-step in CapCut (mobile or desktop)

### 1. Import and align picture

1. New project → 9:16.
2. Import **video** (`final_short.mp4` for reference) OR import each `clips/*.mp4` / stills per `CAPCUT_TIMELINE.md` timestamps.
3. Import **voiceover.mp3** — drag to audio track; lock sync at `0:00`.
4. Match each visual cut to manifest **start** seconds (use `CAPCUT_TIMELINE.md` table).

### 2. Add sound effects track

1. Tap **Audio** → **Sound effects** (or **Sounds** → SFX tab).
2. Add a **second audio lane** below VO for SFX only (keeps mixing clean).
3. For each beat, search and place per `CAPCUT_SFX.md` in the pack (generated per draft).

**Place timing:** scrub to the **visual cut**, then drag the SFX clip so the **attack** lands **1–3 frames before** the cut (about 0.03–0.1s at 30fps).

### 3. Set volumes (starting points)

| Track | Volume | Notes |
|-------|--------|-------|
| Voiceover | 100% | Never bury the hook |
| Diegetic SFX (taps, creaks, UI) | 35–55% | Under VO |
| Ambience / drone | 15–25% | Barely felt |
| Finale stinger | 85–100% | **Finale drafts only** — max 0.3s peak |

Tap clip → **Volume** → adjust. Use **Fade out** 0.05s on micro-cues; **no fade-in** on stingers.

### 4. Duck background music (if used)

**Method A — Auto duck (if available):**  
Select music track → **Audio** → enable **Ducking** / **Auto duck** → strength until VO is clear.

**Method B — Keyframes (precise):**  
On music track at speech start: keyframe volume **80%** → 0.5s later keyframe **25%** → hold through speech → rise back.  
(Full pattern: `videowizardtools.com/keyframes-in-capcut` audio ducking section.)

### 5. False calm (beats 6–7)

- **Mute or delete** risers/drones on this section.
- Keep only **room tone** or silence.
- This contrast makes the finale stinger land (see Kerins / Redfern — silence before loud event).

### 6. Finale vs suspense-replay

| `jumpscare_plan.profile` | Last 3s audio |
|--------------------------|---------------|
| `finale` | Horror **stinger** + optional thump at lunge cut; sync to `CAPCUT_SFX.md` sting time |
| `suspense_replay` | **No stinger** — fade ambience, hold tension, hard end (Shorts replay) |

Check `manifest.json` → `jumpscare_plan` or `jumpscare_plan.json` in pack.

### 7. Export

- **1080×1920**, H.264, 30fps  
- If ffmpeg already rendered `final_short.mp4` with burned captions, use CapCut mainly for **SFX polish** on a duplicate project OR add SFX before final export in hybrid workflow.

---

## CapCut SFX search cheat sheet

| Story beat | Search in CapCut | Diegetic? |
|------------|------------------|-----------|
| Motion alert / hook | `notification`, `camera`, `alert`, `glitch` | Yes |
| App refresh / phone | `tap`, `ui`, `click`, `swipe` | Yes |
| Hallway / alone | `footsteps`, `creak`, `door`, `wind` | Yes |
| Speaker / knock | `knock`, `tap`, `thud` | Yes |
| False calm | *(none — strip layers)* | — |
| Finale lunge | `horror`, `cinematic hit`, `impact`, `stinger` | Mixed |

---

## Quality check before export

- [ ] Hook line audible with zero SFX masking first word  
- [ ] No jump stinger before final 3s (finale profile)  
- [ ] False calm section is noticeably quieter  
- [ ] Finale stinger synced to visual pop (frame-accurate)  
- [ ] Suspense-replay draft has **no** stinger  
- [ ] Mute preview: story still understandable (Jenny mute-safe)
