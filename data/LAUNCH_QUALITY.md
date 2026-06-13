# Launch quality playbook — first 2 Don't Blink Shorts

Goal: **maximize completion rate + jumpscare payoff** on a zero-video channel.

## Topic picks (strongest hooks)

1. Mirror blinked one second after you did
2. Security cam flagged motion — you live alone
3. Last text showed delivered — phone was off
4. Knock came from inside the closet

## Script bar (draft QC)

- Line 1 = **impossible detail** (not "scary story")
- 70–110 words, 6–8 visual beats
- False calm beat ("you told yourself it was nothing")
- Final line cues visual scare — no tagline outro
- `run_quality_checks` must pass before render

## Visual bar (Kling — default)

- `VIDEO_BACKEND=kling` — Kling 3.0 **2×15s**, native character audio
- `VISUAL_STYLE=ai_video` — required for motion path
- Dialogue in script → Kling lip sync; **subtitles burned in post**
- `vision_qc_min_score` default **7.5**

## Audio bar

- **Kling mode:** character voices in clip (no Resemble narrator)
- **Legacy mode:** Resemble VO — tense delivery
- `horror_sfx_enabled=true` — procedural SFX + finale stinger at render
- Title + description: **🔊 volume warning**

## Upload checklist

- [ ] Vision QC pass (no cosy frames, captions in safe zone)
- [ ] `containsSyntheticMedia` declared
- [ ] Hook in title matches line 1 of script
- [ ] Scare type rotated vs previous upload (reflection ≠ knock ≠ glitch)

## After first 2

Read retention in YouTube Analytics — if drop before 20s, tighten escalation beats; if drop at end, strengthen false calm.
