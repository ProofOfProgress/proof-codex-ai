# Kling 3.0 video pipeline — locked in (PERIPHERAL)

**Default backend:** `VIDEO_BACKEND=kling`  
**Model:** `kwaivgi/kling-v3-video` on Replicate  
**Format:** 2 clips × 15 seconds = ~30s Short, **one stitch**

---

## Why Kling

| Need | Kling answer |
|------|----------------|
| ~30s with least stitching | 2 generations, 1 join (not 10 micro-clips) |
| Character voices on screen | Native audio + lip sync (`generate_audio=true`) |
| First-person, no narrator | Dialogue in prompt — no Resemble narrator track |
| Village Eye horror | Multi-shot inside each 15s block |

**Still post-process:** burned-in ASS subtitles + horror SFX sting (Kling is bad at readable on-screen text).

---

## Env (`.env` / Cursor Secrets)

```bash
VIDEO_BACKEND=kling
VISUAL_STYLE=ai_video
AI_VIDEO_GENERATION_ENABLED=true   # owner must opt in for paid Replicate runs
REPLICATE_API_TOKEN=r8_...

KLING_MODEL=kwaivgi/kling-v3-video
KLING_CLIP_SECONDS=15
KLING_CLIPS_PER_SHORT=2
KLING_GENERATE_AUDIO=true
KLING_SKIP_NARRATOR_TTS=true
KLING_MODE=pro          # 1080p
KLING_ASPECT_RATIO=9:16
KLING_MULTI_SHOT=true   # 3 internal cuts per 15s clip
```

**Legacy 10-beat MiniMax/Hailuo:** set `VIDEO_BACKEND=legacy_i2v` and `AI_VIDEO_MAX_BEATS=10`.

---

## Pipeline flow

```
Script (first-person, dialogue in quotes)
  → split into 2 parts (~15s each)
  → Kling clip A (multi-shot, native audio)
  → Kling clip B (uses end frame of A for continuity)
  → ffmpeg concat (1 stitch)
  → extract audio → horror SFX mix
  → burn ASS subtitles from script timing
  → vision QC → upload
```

**Skipped in Kling mode:** Resemble narrator TTS, Gemini transcript sync (captions use script estimate).

---

## Code

| Module | Role |
|--------|------|
| `shorts_bot/production/render_kling.py` | Prompts, split, 2×15s generation |
| `shorts_bot/production/images/replicate.py` | `generate_replicate_kling_video()` |
| `shorts_bot/production/pack.py` | `render_mode=kling_clips` |
| `shorts_bot/production/render_video.py` | Concat + SFX + captions |
| `shorts_bot/config.py` | `VIDEO_BACKEND`, Kling settings |

---

## Owner test (one Short)

1. Set `AI_VIDEO_GENERATION_ENABLED=true` in Cursor Secrets (costs ~2 Replicate runs).
2. Run: `python3 -m shorts_bot.production.daily_cli --topic "village eye dream" --no-upload`
3. Compare `data/production/draft_N/final_short.mp4` locally before upload.

Post time target: **8 AM** owner local (configure `AUTO_DAILY_HOUR` in `.env`).
