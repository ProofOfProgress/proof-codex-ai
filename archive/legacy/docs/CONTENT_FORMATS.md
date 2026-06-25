# Content formats — Shorts + long-form without runaway video cost

**Brand:** Peripheral  
**Default now:** `short_30` (discovery Shorts)  
**Strategy:** Shorts find the audience; long-form monetizes watch time — **reuse assets**, cap I2V.

---

## Why both Short and long

| Format | Job | Cost profile |
|--------|-----|--------------|
| **Shorts** | Discovery, cluster proof, binge | Low per video if hybrid |
| **Long (8–12 min)** | Watch hours, YPP RPM, search depth | High if full I2V — **must budget** |

YouTube rewards **topic authority** across formats. Shorts that retain feed the long-form matcher — but long-form does **not** need 40 I2V clips.

---

## Format profiles (code: `content_format.py`)

| ID | Length | Aspect | Max I2V beats | Visual | New Replicate? |
|----|--------|--------|---------------|--------|----------------|
| `short_30` | ~30s | 9:16 | 10 (capped by settings) | ai_video | Yes — launch quality |
| `short_hybrid` | ~30s | 9:16 | **3** | hybrid | Hook + finale (+1 mid) |
| `long_compilation` | 8–15 min | 16:9 | **0** | stitch | **No** — reuse Short MP4s |
| `long_still` | 5–12 min | 16:9 | **0** | Ken Burns stills | Stills only (FLUX cheap) |
| `long_hybrid` | 8–15 min | 16:9 | **4** | hybrid | Reuse Short clips + few heroes |

Set in `.env`:

```bash
CONTENT_FORMAT=short_hybrid   # day-to-day cheap Shorts
# CONTENT_FORMAT=long_compilation  # when stitching 3 Shorts into one upload
```

---

## Cost ladder (recommended rollout)

### Phase 1 — Now (Shorts only, cheap)

```bash
AI_VIDEO_GENERATION_ENABLED=true   # when quota allows
CONTENT_FORMAT=short_hybrid
VISUAL_STYLE=hybrid
AI_VIDEO_MAX_BEATS=3
```

- **~3 Replicate I2V calls** per Short (hook, optional mid, finale)  
- Middle beats: **cached FLUX still → Ken Burns** (already in `render_video.py`)  
- **~70% cost cut** vs 10-beat full motion  

### Phase 2 — First long-form (zero new I2V)

**`long_compilation`** — “3 Peripheral stories that’ll keep you up”

1. Pick 3 best-performing Shorts (retention winners).  
2. Write 30s bridge VO between each (same narrator).  
3. ffmpeg: 16:9 letterbox or blur-background stack of 9:16 Shorts.  
4. **No new I2V** — only VO + edit.

*Pipeline prep: reuse `clips/` from draft packs; assembly CLI TBD.*

### Phase 3 — Story-time long (stills only)

**`long_still`** — 8 min single story

1. Expand Short script to 800–1200 words (same pillar).  
2. **FLUX still every 20–40s** of VO (~15–20 stills).  
3. Ken Burns + captions — **no I2V**.  
4. Cost ≈ still image gen only.

### Phase 4 — Premium long (rare)

**`long_hybrid`** — breakout topic only

- Reuse 3–5 Short **clips** as B-roll (9:16 crop in 16:9).  
- **Max 4 new I2V** beats (hook, 2 escalation, finale).  
- Cap with `effective_max_i2v_beats()` in code.

---

## Hybrid visual stack (already in repo)

| Piece | Technology | Cost |
|-------|------------|------|
| Stills | Replicate FLUX / Fal schnell | Low |
| Motion (few beats) | MiniMax / Hailuo I2V | High per clip |
| Middle beats | `_still_to_clip` Ken Burns | **Free** |
| Captions | ffmpeg ASS | Free |
| VO | Resemble / edge | Fixed per minute |
| Overlays | CCTV OSD composited | Free |

`select_i2v_beat_indices()` always picks **hook + finale** when capped.

---

## Short → long funnel (no duplicate spend)

```
Short script (30s) ──► publish Short
        │
        ├─► Winner? ──► expand script to 6–8 min (long_still)
        │
        └─► 3 winners? ──► compilation (long_compilation, $0 I2V)
```

**Never** regenerate 10 I2V clips for a story you already Short'd.

---

## Aspect ratio

| Format | Production note |
|--------|-----------------|
| Shorts | 9:16 native |
| Long compilation | Letterbox 9:16 in 16:9 **or** blur fill — no regen |
| Long still/hybrid | Generate **16:9 FLUX stills** for new beats; reuse 9:16 clips cropped |

Landscape I2V is expensive — prefer **still + pan** for long-form until revenue justifies.

---

## Config quick reference

| Variable | Purpose |
|----------|---------|
| `CONTENT_FORMAT` | Profile id from table above |
| `AI_VIDEO_MAX_BEATS` | Global ceiling (format may lower) |
| `AI_VIDEO_GENERATION_ENABLED` | Master kill switch |
| `VISUAL_STYLE` | `hybrid` forces still fallbacks between I2V |

---

## Research

`data/research/PERIPHERAL_SHORT_LONG_HYBRID_STRATEGY.md` — economics, audience, when to flip formats.
