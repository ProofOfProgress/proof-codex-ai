# CapCut template — Don't Blink horror

> **Superseded for SFX detail:** use `capcut_horror_sfx.md` + per-pack `CAPCUT_SFX.md`.

## New project defaults

- Ratio: **9:16**
- Length: **25–35 seconds**
- FPS: **30**

## Layers (top to bottom)

1. **Video** — I2V clips per `CAPCUT_TIMELINE.md` (or import `final_short.mp4`)
2. **Voiceover** — `voiceover.mp3`, locked at 0:00
3. **SFX lane** — per `CAPCUT_SFX.md` (diegetic cues + finale stinger only on finale drafts)
4. **Captions** — burn-in from ffmpeg OR CapCut import `captions.srt` — **Jenny 05 safe zone** (~320px above bottom)
5. **Ambience/music** (optional) — YouTube Audio Library, horror drone at low level

## Audio rules

- **VO first** — always clearest element
- **SFX under VO** except finale stinger (0.2–0.3s peak)
- **False calm** — strip SFX layers (silence = contrast)
- **Duck music** under speech (auto-duck or volume keyframes)
- Research: `data/research/HORROR_SOUND_EFFECTS_RESEARCH.md`

## Export

1080×1920, H.264, upload as Short
