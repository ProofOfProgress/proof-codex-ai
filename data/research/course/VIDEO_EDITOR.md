# Video editor (owner override)

**Course tool:** CapCut desktop (free)  
**We use:** **AI-agent video editor** — automate the same logic, no manual CapCut.

## Pipeline (affiliate posts)

1. Input: 5s Kling clip (Module 5)  
2. **Pan loop:** forward + reverse → ~10s (`video_variants.make_pan_loop_clip`)  
3. **Burn-in caption:** on-screen hook text, full clip length (styling below)  
4. Module 1 QC → upload  

---

## On-screen captions (owner — ever-changing)

**Captions change often** — like products. This template is what we use **right now**. Group calls and owner updates beat stale copy. When the template changes, update this file first, then `video-caption-writer` subagent and `shorts_bot/tiktok_shop/captions.py`.

### Copy template (current)

```
I am SO sorry if you already grabbed {product} because the discount is huge today
```

- **`SO`** stays capitalized  
- **`{product}`** = product name with **each word capitalized** (title case)  
  - Example product: `pre workout powder` → **Pre Workout Powder**  
  - Full line: *"I am SO sorry if you already grabbed a Pre Workout Powder because the discount is huge today"*  
- Include **"a"** before the product name when it reads naturally (as in the sample)

Code helper: `shorts_bot.tiktok_shop.captions.on_screen_caption(product_name)`

### Burn-in styling (current)

| Setting | Value |
|--------|--------|
| Text | **White**, bold |
| Outline | **Tiny black outline** — no big background bubble |
| Placement | Upper-center (~top third) |
| Duration | Full loop clip (~10s) |

Automated in `video_editor.burn_on_screen_caption()` — white text + thin black border, **no box**.

*(Course CapCut demo used white box + black text — we override to outline-only.)*

---

## On-screen copy vs other prompts

| Type | Source |
|------|--------|
| Kling motion prompt | **Product Video Prompt Builder** — `PROMPT_BUILDER.md` (Module 1 compliant) |
| Image prompt | Module 4 product image workflow |
| **On-screen caption** | **This file** → `video-caption-writer` subagent |

Prompt copy changes often — group calls win over stale templates.
