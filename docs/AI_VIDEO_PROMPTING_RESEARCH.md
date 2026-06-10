# AI video prompting research — high-quality Shorts (2026)

One-hour research synthesis for **Soft Continuity** — cosy faceless mental-health Shorts, 9:16, caption-safe.

**Sources:** [VidScore AI video prompt guide](https://vidscore.dev/blog/ai-video-prompt-guide), [AI Magicx director framework](https://www.aimagicx.com/blog/ai-video-prompt-engineering-advanced-guide-2026), [ImageToPrompt model guide](https://www.imagetoprompt.dev/blog/video-prompt-guide-2026/), [Kling prompt guide](https://kling.ai/blog/kling-ai-prompt-guide), [Promptolis production patterns](https://promptolis.com/blog/ai-video-generation-prompts-higgsfield-runway-luma-2026/), [temporal consistency](https://prompting.systems/blog/prompts-for-maintaining-temporal-consistency-in-ai-video), [Shorts timing blueprint](https://aiimagetovideo.pro/blog/ai-prompt-for-creating-viral-videos-on-youtube/), codebase audit (`image_prompts.py`, `render_video.py`, `cosy_aesthetic.md`).

---

## Executive summary

| Question | Answer for Soft Continuity |
|----------|---------------------------|
| **Best quality path today?** | Keep **stick figure + ffmpeg** (draft 9) for captions + cost; use **AI video for 2–3 hero clips only** |
| **Best AI video workflow?** | **Image-to-video (I2V)** from FLUX cosy stills — not pure text-to-video per beat |
| **Prompt length?** | **40–120 words** per clip; one visible action per 3–5s clip |
| **#1 quality killer?** | Uncontrolled camera — use `locked camera` or `slow push-in` unless motion is the story |
| **Continuity trick?** | **END STATE** in clip N = **CONTINUITY IN** for clip N+1; last frame → next start frame |

---

## Universal 5-part framework (all models)

Every clip prompt should include:

| Part | What to write | Soft Continuity example |
|------|---------------|-------------------------|
| **Subject** | One faceless subject or prop | Hands on phone, silhouette on couch, mug steam |
| **Action** | One clear motion | Thumb hovers, shoulders breathe, steam rises |
| **Camera** | Shot + movement | Medium static, slow push-in, locked tripod |
| **Environment** | Cosy set | Cream wall, rain window, terracotta couch, lamp glow |
| **Style** | Look + constraints | Minimal illustration, warm grain, no faces, 9:16 |

**Negative block (always):** `no faces, no text, no watermark, no logos, morphing textures, camera shake, extra fingers, horror, office fluorescent`

---

## Model-specific tuning (2026)

| Model | Prompt style | Duration | Best for |
|-------|--------------|----------|----------|
| **Kling 3** | Rich detail, physics verbs, multi-shot labels | 5–15s | Long coherent clips, multi-beat |
| **Runway Gen-4** | Mood first, then composition; use **camera panel** for moves | 5–10s | Cinematic B-roll, atmosphere |
| **Veo 3.1** | Concise, motion-forward; dialogue in quotes for audio | ~8s | Photoreal hero shots |
| **Pika** | Short + style keyword (`watercolor`, `minimal`) | 3–5s | Stylized tests, fast iteration |
| **Luma Dream Machine** | Natural flowing sentences | 5s | Realistic scenes, beginners |
| **Minimax Hailuo** | Narrative sentences, not keyword lists | 5–6s | Story beats |

**Production routing:** B-roll / transitions → Pika or Luma; hero hook → Runway or Kling; lip-sync dialogue → Veo/Grok (not our faceless stack).

---

## Shorts timing blueprint (retention)

For 26–45s mental-health Shorts:

| Window | Job | Prompt focus |
|--------|-----|--------------|
| **0–2s** | Hook | Conflict visible in frame 1 — phone glow, hunched silhouette |
| **2–8s** | Problem loop | Locked camera, same room, escalating micro-action |
| **8–22s** | Protocol beats | One action per clip — timer, breath, mug, phone down |
| **22–26s** | Payoff | Stillness + lamp; room for caption CTA |

**Rule:** One visible action per clip. Models drift when asked for multiple actions.

---

## Soft Continuity VISUAL DNA (paste unchanged)

```
VISUAL DNA — Soft Continuity:
Style: polished minimal illustration, soft film grain, not photoreal, not 3D, not anime.
Palette: cream #F5EFE6, floor #E8DFD4, sage #9DB8A0, terracotta #C9A08A, lamp #F2D98A, rain #A8B8C8.
Lighting: warm floor lamp key, soft shadows, no fluorescent.
Composition: 9:16; action upper 55%; bottom 40% empty for captions + Shorts UI.
Faceless: hands, silhouettes from behind, POV only — no faces.
Motion: slow push-in or static; meditative, not TikTok frantic.
Negative: no text, watermark, logos, faces, horror, morphing, camera shake.
```

---

## Soft continuity workflow (clip chaining)

Industry “soft continuity” = gentle handoff between AI clips:

1. Generate **Clip 1** with full VISUAL DNA + SCENE + END STATE  
2. Export **last frame**  
3. **Clip 2** = I2V with that frame + `CONTINUITY IN: [END STATE]`  
4. ffmpeg: 0.3–0.5s cross-dissolve between clips (optional)  
5. Burn captions once in ffmpeg ASS (y≈1520) — **never text in AI prompts**

This matches brand name *Soft Continuity* and avoids identity drift from pure T2V.

---

## Hybrid stack recommendation (this repo)

**Today (production):**
```
Gemini script → Resemble → TurboScribe → stick frames OR FLUX stills → ffmpeg Ken Burns → ASS captions
```

**Upgrade path (AI video without caption bugs):**

| Tier | Use | Tool |
|------|-----|------|
| **A — Default** | All protocol beats | Stick figures (`VISUAL_STYLE=stickfigure`) |
| **B — Premium hook** | 0–3s only | FLUX still → Kling/Runway I2V 3s |
| **C — Full AI** | Entire Short (expensive) | 6–8 I2V clips chained + dissolves |

**Why not full AI video yet:** No video provider in repo; caption safe zone requires bottom 40% clear; stick figures already pass QC.

---

## Ten production templates

See `shorts_bot/production/ai_video_prompts.py` — `visual_dna()`, `templates()`, `segment_to_video_prompt()`.

Templates cover:

1. Sunday couch phone hook  
2. Timer instead of scroll  
3. Three breaths grounding  
4. 3am bed insomnia  
5. Rainy window overthinking  
6. Before dreaded text reply  
7. Door before party  
8. Shame spiral couch huddle  
9. Low-spoon mug micro-win  
10. Payoff ring / lamp stillness  

---

## Common mistakes → fixes

| Mistake | Fix |
|---------|-----|
| Vague “person feeling anxious” | Specific prop + action: “thumbs hover over phone on terracotta couch” |
| Camera unspecified | `locked tripod` or `slow 10% push-in over 4s` |
| Multiple actions per clip | Split into 2 clips with END STATE linking |
| Text in AI video | Captions in ffmpeg only; add `no text` to negative |
| Faces for “relatability” | Silhouette / hands POV — faceless is the brand |
| 120s of continuous T2V | 6–8 × 3–5s clips max |
| Ignoring bottom safe zone | `bottom 40% empty` in every prompt |
| Office aesthetic | Cosy home: couch, lamp, rain — see `cosy_aesthetic.md` |

---

## Code integration (added)

| File | Purpose |
|------|---------|
| `shorts_bot/production/ai_video_prompts.py` | VISUAL DNA + per-segment video prompts |
| `docs/AI_VIDEO_PROMPTING_RESEARCH.md` | This doc |
| Manager underlings | Research priority can score AI video vs stick ROI |

**CLI test one prompt:**
```bash
python3 -m shorts_bot.production.ai_video_prompts_cli "the minute before you check your phone from the couch on Sunday"
```

---

## 1-hour research queue (manager underlings)

When you say `take an hour to research AI video prompting`, underlings run:

1. Research Lead — queue plan  
2. Deep research — competitor Shorts + tool landscape  
3. Hook Analyst — 5 hook variants per cosy topic  
4. Niche Strategist — stick vs AI video ROI per topic  
5. Trends Scout — “AI mental health shorts” query volume  

Output: `data/research/*.json` + manager summary. Internal log: `data/underlings/work.log`.

---

## Next build steps (when ready)

1. `ai_segment_to_video_prompt()` wired when `VISUAL_STYLE=ai_video`  
2. Provider module: Fal `fal-ai/kling-video` or Replicate video model  
3. `export_last_frame()` + I2V chain in pipeline  
4. ffmpeg `xfade` cross-dissolve between clips  
5. Video QC: face detector, text-in-frame reject  

---

## Verdict for Soft Continuity

**Highest quality per dollar right now:** cosy stick figures + TurboScribe sync + ASS captions at y=1520 (draft 9 bar).

**Highest quality per “wow”:** Template 1 (couch phone hook) as **single** Runway/Kling I2V clip → hard cut to stick protocol beats.

Do not replace the whole Short with AI video until continuity chain + caption QC are automated.
