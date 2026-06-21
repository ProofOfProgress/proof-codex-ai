# Peripheral — Short + long-form hybrid strategy (cost-aware)

**Assessed:** 2026-06-12  
**Companion:** `docs/CONTENT_FORMATS.md`, `shorts_bot/production/content_format.py`  
**Owner goal:** Discovery via Shorts + watch hours via long-form **without** runaway Replicate I2V bills.

---

## Executive summary

**Best bet:** Run **both** — Shorts for discovery, long-form for money — but **never pay twice for the same story**.

| Layer | Format | Video gen spend |
|-------|--------|-----------------|
| Discovery | 30s Shorts (`short_hybrid`) | **2–3 I2V clips** + stills |
| Depth | 8–12 min compilation (`long_compilation`) | **$0 I2V** — stitch 3 Shorts |
| Story-time | 5–12 min narrative (`long_still`) | **Stills only** |
| Premium | 8–12 min hybrid (`long_hybrid`) | **≤4 I2V** + reuse Short clips |

Full-motion every beat on a 10-minute video ≈ **40–80×** the cost of one hybrid Short. That is not sustainable pre-revenue.

---

## Part 1 — Why hybrid channel architecture wins

### 1.1 What each format does for Peripheral

| Format | Algorithm job | Revenue job |
|--------|---------------|-------------|
| **Shorts** | Seed pool, topic cluster, new subs | Shorts ad fund (smaller), **funnel** |
| **Long** | Search, suggested, session time | **YPP watch hours**, higher RPM |

Shorts viewers who subscribe are **pre-qualified** for long horror. Long videos deepen **topic authority** in the same cluster (faceless horror / scary stories).

### 1.2 Industry pattern (2026)

- Shorts = **top of funnel** (TikTok-style swipe)  
- Long = **library + revenue** (search + TV-style viewing)  
- Successful faceless horror channels often use **still + VO** or **compilation** for long before investing in heavy animation.

---

## Part 2 — Cost anatomy (Replicate I2V)

### 2.1 Per-Short economics (rough order of magnitude)

| Mode | I2V calls | Relative cost |
|------|-----------|---------------|
| Full `short_30` (10 beats) | 10 | **$$$$** |
| `short_hybrid` (3 beats) | 3 | **$** |
| Still-only Short | 0 | **¢** (FLUX stills only) |

**Default recommendation:** `CONTENT_FORMAT=short_hybrid` + `AI_VIDEO_MAX_BEATS=3` for daily ops. Reserve full 10-beat for **breakout pillar** tests only.

### 2.2 Per-long-form economics

| Mode | I2V | Stills | Edit |
|------|-----|--------|------|
| `long_compilation` | 0 | 0 | ffmpeg stitch + bridge VO |
| `long_still` (10 min) | 0 | ~18 | Ken Burns |
| `long_hybrid` | 4 | ~10 | reuse Short clips |

**First long upload should be `long_compilation`** — proves watch time with **zero** new video gen.

---

## Part 3 — Production workflows (no waste)

### 3.1 Short (daily engine)

1. Script 70–110 words, 6–8 beats.  
2. VO + transcript.  
3. FLUX still **every** beat (cheap).  
4. I2V **only** indices from `select_i2v_beat_indices` (hook + finale + sampled mid).  
5. Render hybrid → publish.  

Code path: `render_ai_video.py` + `render_video.py` still fallback.

### 3.2 Long compilation (first long-form)

**Title example:** “3 scary stories for people home alone at night | Peripheral”

1. Select 3 Shorts with best **retention at end**.  
2. Script bridges: 2–3 sentences between stories (same VO).  
3. ffmpeg concat: `[intro VO + Short1] [bridge + Short2] [bridge + Short3] [outro CTA]`.  
4. 16:9: blurred background + centered 9:16 **or** full-width crop of high-action moments only.  
5. Chapters in description (timestamps).  

**Cost:** one Resemble VO session for bridges only.

### 3.3 Long still narrative (expand a winner)

When one Short hits **outlier retention**:

1. Expand hook into 6–8 min script (same pillar).  
2. 15–25 FLUX **16:9** stills (no I2V).  
3. Ken Burns + captions.  
4. Pin comment linking back to original Short.

### 3.4 Long hybrid (later, selective)

- Import `clips/*.mp4` from Short pack as B-roll.  
- New I2V only for **landscape hero** moments (max 4).  
- `CONTENT_FORMAT=long_hybrid`.

---

## Part 4 — When to switch formats

| Signal | Action |
|--------|--------|
| Shorts retain but RPM low | Start **long_compilation** monthly |
| One Short 5× average views | Expand to **long_still** same story |
| YPP approved + stable uploads | 1 long / month + daily Shorts |
| Replicate bill spikes | Force `short_hybrid` globally |
| Upload quota tight | Shorts only; batch long in edit |

---

## Part 5 — Audience alignment across formats

Same **Peripheral** cluster for both:

- Short hook = long chapter title energy  
- Long description links Short playlist  
- Pinned Short on long upload  
- Comment CTA: “Watch the Short version” / “Full story here”

Do **not** go vlog or podcast — breaks horror cluster.

---

## Part 6 — Roadmap (code + ops)

| Phase | Deliverable | I2V spend |
|-------|-------------|-----------|
| **Now** | `content_format.py` profiles + docs | Config only |
| **Next** | `long_compilation_cli` — stitch 3 draft MP4s | $0 |
| **Later** | `long_still` pack builder (16:9 stills) | Stills |
| **Later** | Chapter/timestamp auto in upload meta | $0 |

---

## Part 7 — Config cheat sheet

```bash
# Cheap daily Shorts
CONTENT_FORMAT=short_hybrid
VISUAL_STYLE=hybrid
AI_VIDEO_MAX_BEATS=3
AI_VIDEO_GENERATION_ENABLED=true

# First long (no new I2V)
CONTENT_FORMAT=long_compilation

# Expanded story (stills only)
CONTENT_FORMAT=long_still
AI_VIDEO_GENERATION_ENABLED=false
```

---

## TL;DR

- **Short + long is correct** — Shorts discover, long earns hours.  
- **Don’t pay twice** — compile Shorts or reuse clips.  
- **Cap I2V** — 3 beats per Short, 0–4 per long.  
- **First long** = compilation of your best 3 Shorts, **$0** new Replicate video.
