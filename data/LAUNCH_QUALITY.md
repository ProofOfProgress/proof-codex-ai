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

## Visual bar (ai_video)

- `VISUAL_STYLE=ai_video` — FLUX still → MiniMax I2V per beat
- Horror templates in `ai_video_prompts.py` — no cream/cosy DNA
- Final segment forced to `jumpscare_lunge` template
- `vision_qc_min_score` default **7.5** (set `8.0` in `.env` for launch week)

## Audio bar

- Resemble VO — tense second-person delivery
- `jumpscare_sting_enabled=true` — synthetic sting on last ~2.5s at render
- Title + description: **🔊 volume warning**

## Upload checklist

- [ ] Vision QC pass (no cosy frames, captions in safe zone)
- [ ] `containsSyntheticMedia` declared
- [ ] Hook in title matches line 1 of script
- [ ] Scare type rotated vs previous upload (reflection ≠ knock ≠ glitch)

## After first 2

Read retention in YouTube Analytics — if drop before 20s, tighten escalation beats; if drop at end, strengthen false calm.
