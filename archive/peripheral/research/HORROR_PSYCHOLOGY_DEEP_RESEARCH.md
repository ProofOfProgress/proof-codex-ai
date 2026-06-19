# Horror deep research — Don't Blink (2026-06-11)

Sources: pipeline `deep_research_topic` (3 runs), web/academic synthesis (predictive processing, tension models, short-form horror craft), competitor Shorts patterns.

---

## 1. What makes horror scary (mechanisms)

### Prediction error (brain science)
The brain constantly predicts the next sensory moment. Horror works when **reality violates prediction** — not random shock, but a **pattern that breaks**.

- **Micro-disruption:** familiar scene → one detail wrong (timestamp, reflection, hallway length). Creates a question mark, not yet fear.
- **Prediction error → amygdala:** unexpected salient stimuli trigger fight/flight (adrenaline, attention lock). Jump scares synchronize across viewers when timing is shared.
- **Recreational fear:** viewers know they're safe; arousal becomes **play/rehearsal**. Sweet spot = enough threat to engage, not so much it's aversive.

### Imagination > monster
**What you don't show** often beats CGI. Closed door creaking > creature reveal. Brain fills the gap with personal fears.

### Uncanny / wrongness
Horror in Shorts wins on **slightly wrong familiar**:
- smile held one second too long
- wave from your own window
- photo timestamp from the future
- mirror blinks after you do

### Universal fear layers (stackable in 30s)
1. Sensory startle (loud sting + motion)
2. Unknown / stranger
3. Loss of control (locked in, can't mute call)
4. Social violation (wrong text from dead contact)
5. Existential wrongness (impossible geometry)

---

## 2. Psychological tension — how to build it

### Tension model (domain-independent)
Tension = **conflict + uncertainty + emotional stakes about a future event**. Suspense is predictive: audience simulates bad outcomes.

**Don't Blink beat map (25–35s):**

| Phase | Seconds | Job |
|-------|---------|-----|
| Hook | 0–3 | Impossible detail — stop scroll |
| Pattern | 3–12 | Establish normal, then fracture it |
| Escalation | 12–20 | Sound + visual micro-cues, each beat new wrong detail |
| False calm | 20–26 | Quiet VO, slow motion — **safety signal** (makes next hit harder) |
| Jumpscare | 26–30 | Full-frame + audio sting |
| Linger | optional 1s | Glitch or black — no explanation |

### Hitchcock principle
**Audience knows bomb is under table** — scare is anticipation, not explosion. For Shorts: hook tells them *something is wrong*; middle is waiting for confirmation.

### Symphony of silence
Build ambient dread (drone, breath, tick) → **cut to silence** → hit. Silence = held breath. Our false-calm beat does this visually + vocally.

### Sound leads, image follows
Underscore tension with:
- warped music box one note
- notification glitch loop
- breath on muted call
- 0.5–1.5s silence before sting

Mute-first Shorts: **scare must read visually**; audio amplifies.

### Write backwards
Pick **final scare image first**, then every beat serves it. No filler beats.

### Loop escalation
Tiny reveal → bigger emotional hit → need to resolve → repeat until overload at end. Each cut = new information + worse implication.

---

## 3. Jumpscare craft (Don't Blink signature)

### Earned vs cheap
- **Earned:** pattern + false calm + misdirection → sting
- **Cheap:** random scream, no setup → reports, mutes, skips

### Timing
- Psycho shower: **calm before** makes jump land. Same for Shorts beat 6–7.
- Misdirection: camera looks left, scare from right / fill frame.

### Rotate scare types (avoid predictable channel)
- face lunge fill frame
- wrong reflection snap
- door slam + silhouette
- glitch morph
- POV something behind you

### Volume
Loud **0.1–0.3s** sting, not 5s clipping. Title/description 🔊 warning.

---

## 4. Short-form horror (TikTok/Shorts specific)

- **0–3s sacred** — unsettling sound, wrong visual, or impossible text line
- **Imply, don't explain** — last image haunts; cut to black
- **Pacing:** new stimulus every 2–3s or swipe
- **Captions synced word-by-word** — holds attention on mute

---

## 5. Applied to our pipeline

| Lever | Implementation |
|-------|----------------|
| Hook | `niche.py` DEFAULT_TOPICS — impossible details |
| Visuals | `ai_video` I2V — hallway, mirror, phone, final lunge |
| Tension | Script beats 6–8 with false calm in generator prompts |
| Scare | Final segment longer I2V prompt + audio sting in render |
| Voice | Resemble cold narrator, whisper on calm beat |
| QC | Vision QC rejects cosy/brights, no stick figures |

---

## 6. What NOT to do

- Gore, real victims, child harm
- 60s slow burn in a 30s format
- Same monster + same sting every upload
- Cosy palette, stick figures, self-help tone
- Over-explain the twist

---

## 7. Research runs saved

- `what-makes-horror-scary-psychological-tension-filmmaking-shorts.json`
- `psychological-tension-dread-buildup-horror-writing-techniques.json`
- `jumpscare-timing-misdirection-neuroscience-recreational-fear-sweet-spot.json`

---

## 8. Academic references (for agents)

- Predictive processing & horror engagement (PMC10725765)
- General psychological model of tension and suspense (PMC4324075)
- Neurobiology of horror cinema — recreational fear, amygdala sync on jump scares (Projections 2024)
