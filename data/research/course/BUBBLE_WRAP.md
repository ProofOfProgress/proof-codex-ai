# Bubble wrap growth (0 → 1k followers)

**Track:** Account warming — **not** affiliate product posts (see Modules 3–8).  
**Current focus:** Run this until each account hits **~1,000 followers**.

## Sound (required)

https://www.tiktok.com/music/original-sound-7418286946344340256  

*(TikTok: **original sound - •Mackenzie•**)*

---

## Video format — always a 2-image slideshow

Posts are **TikTok photo slideshows** (not one image). **Two slides every time.**

### Slide 1 — hook only

- **Visual:** Subject **covered in bubble wrap** (frog, cake, soccer jersey, duck, etc.)
- **Text:** Hook only — no interaction lines on this slide  
- **Patterns:**
  - `[SUBJECT] BUBBLE WRAP ASMR >>>`
  - `bubble wrap asmr>>>>`
  - `perfect for people with ADHD`
  - `POP [SUBJECT] BUBBLE WRAP` (+ optional ⚽ etc. if it fits the subject)

**Style:** Bold white text, thick black outline, centered.

### Slide 2 — interaction → pop

Same wrapped subject (or companion image). **Only** the engagement list:

```
Pause = Pop 💥
Follow = Loud pop 🔊
Share = Giant pop 🦖
Comment = Big pop 💥💥
```

Line order and exact words can match what’s viral on the sound page — keep the **action = pop size** pattern.

### Emoji rules (owner)

| Pop size | Emojis |
|----------|--------|
| Small | 💥 (1) |
| Medium | 💥💥 or one strong icon |
| **Big / giant / loud** | 🔊 (volume), 🦖 (T-rex), 🐆, etc. — **loud/intense vibes** |

- **Other emojis are OK** if they fit the **pop intensity** — not random.
- **Do NOT** use unrelated object emojis (e.g. 🥧 pie for “giant pop”) **unless** the subject is literally that thing in bubble wrap (bubble-wrapped pie → pie emoji is fine).
- No 🫧 bubble emoji for pops — use 💥 / 🔊 / 🦖 style.

---

## Sample references

- **Owner samples (11 PNGs):** [Google Drive](https://drive.google.com/drive/folders/1drt1xcaakCDMQ2ABJsJpeOYW7XDnHqDB) · catalog: `BUBBLE_WRAP_SAMPLES.md`  
- Local: `data/research/course/_media/bubble_wrap/samples/`  
- Reference account: [@buck.finds](https://www.tiktok.com/@buck.finds)  
- Full Loom: `module_02_best_practices.md`

---

## Checklist

1. Create account with **aged email**  
2. **Day 1:** open bubble sound — study top slideshows  
3. Bubble-themed username + bio (“follow for loud pop”)  
4. **Slide 1:** unique wrapped-subject image + hook text only  
5. **Slide 2:** same subject (or variant) + interaction/pop lines + emojis  
6. Post as **2-photo slideshow** + **Mackenzie sound**  
7. **4 growth accounts** in parallel until **~1k each** — split posting cadence (owner 6/2026):  
   | Tier | Accounts | Posts/day each |
   |------|----------|----------------|
   | **Safe** | 2 | **3–4** |
   | **Aggressive** | 2 | **8–10** |
8. **Later:** 1k → 5k → `ADS_1K_TO_5K.md`  
9. **Affiliate account:** Modules 3–8 + full bot pipeline when owner starts revenue posts (parallel to bubble growth)  

Live changes → owner reports on `GROUP_CALLS.md`.

---

## Posting format — manual swipe (critical)

Bubble wrap posts must be TikTok **photo carousels** (Photo Mode) — the viewer **swipes** slide 1 → slide 2 themselves.

| ✅ Correct | ❌ Wrong |
|-----------|---------|
| **2-photo carousel** — manual swipe | MP4 video that **auto-advances** between frames |
| Native TikTok slideshow / photo mode | Stitched slideshow exported as one video file |

**Do not** export a single auto-playing video for bubble wrap. That is not the same format as viral posts on the sound page.

### Can the bot API do this?

**Yes — TikTok Content Posting API supports photo carousels** (`media_type: PHOTO`, 2–35 images) via:

`POST /v2/post/publish/content/init/`

Our repo **does not implement this yet** — today we only upload **MP4 video** (`/v2/post/publish/video/init/`). Bubble wrap needs a new **`upload_photo_carousel`** path.

### Mackenzie sound + API (important)

The API **cannot attach a specific TikTok sound ID** (like Mackenzie) on direct photo post. Options:

| Mode | What happens |
|------|----------------|
| **`MEDIA_UPLOAD`** (recommended for bubble wrap) | 2 images land in TikTok **inbox as draft** → open in app → add Mackenzie sound → publish |
| **`DIRECT_POST`** | Goes live immediately but only **`auto_add_music`** — **not** the required sound |

**Practical workflow:** bot uploads 2-image carousel to **inbox** via Zernio → finish on **that account’s phone hub slot** (add Mackenzie sound → publish). See `docs/FOR_OWNER_PHONE_HUB.md`.
