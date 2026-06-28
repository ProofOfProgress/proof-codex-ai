# Video editor (owner override)

**Course tool:** CapCut desktop (free)  
**We use:** **TikTok native on-screen text** (preferred) or optional ffmpeg burn-in.

## Pipeline (affiliate posts)

1. Input: 5s Kling clip (Module 5)  
2. **Pan loop:** forward + reverse → ~10s (`video_variants.make_pan_loop_clip`)  
3. **On-screen hook:** TikTok app text **or** burn-in (see below)  
4. Module 1 QC → upload  

---

## On-screen hook delivery

| Mode | Config | What happens |
|------|--------|--------------|
| **`native`** (default) | `TIKTOK_SHOP_HOOK_DELIVERY=native` | Clean MP4 + `.hook.txt` beside clip — **add text in TikTok** |
| `burn_in` | `TIKTOK_SHOP_HOOK_DELIVERY=burn_in` | Bot burns white text via ffmpeg (legacy) |

---

## Line length rule (owner locked)

**Max 18 characters per line** — never wider. 26 and 22 still clipped on 9:16; 18 leaves safe side margin.

| Setting | Default |
|---------|---------|
| `TIKTOK_SHOP_CAPTION_MAX_CHARS_PER_LINE` | **18** |
| `TIKTOK_SHOP_CAPTION_MAX_LINES` | 7 |

Preview wrapped lines:

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli hook-lines --product "Car Phone Mount"
```

Code: `shorts_bot/tiktok_shop/captions.py` → `wrap_hook_lines()`

---

## On-screen captions (owner — ever-changing)

**Captions change often** — like products. Update this file first, then `video-caption-writer` and `captions.py`.

### Copy template (current)

```
I am SO sorry if you already grabbed {product} because the discount is huge today
```

- **`SO`** stays capitalized  
- **`{product}`** = title case each word  
- Use **"a"** before the product when it reads naturally  

### Example wrapped at 18 chars/line

```
I am SO sorry if
you already
grabbed Insulated
Tumbler because
the discount is
huge today
```

Sidecar file: `data/tiktok_shop/clips/{name}_loop.hook.txt`

### TikTok native text (preferred)

1. Upload / post the **loop MP4** (no burned text)  
2. Open TikTok editor → **Text**  
3. Paste **one line at a time** from `.hook.txt` (each line ≤18 chars)  
4. Style: white text, thin outline, upper third — match course look  

### Burn-in styling (only if `burn_in` mode)

| Setting | Value |
|--------|--------|
| Text | **White**, bold |
| Outline | **Tiny black outline** |
| Font size | 42 (config) |
| Placement | Upper-center (~top third) |

---

## On-screen copy vs other prompts

| Type | Source |
|------|--------|
| Kling motion prompt | **Product Video Prompt Builder** — `PROMPT_BUILDER.md` |
| Image prompt | Module 4 product image workflow |
| **On-screen hook lines** | **This file** → `video-caption-writer` → `wrap_hook_lines()` |

Prompt copy changes often — group calls win over stale templates.
