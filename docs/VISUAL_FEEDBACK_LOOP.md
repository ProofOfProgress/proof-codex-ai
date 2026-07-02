# Visual feedback loop — Gemini ↔ prompt builder ↔ Kling

**Problem:** Module 1 QC catches violations but doesn’t help you **fix the prompt** when motion looks static or the clip isn’t commercial-ready.

**Solution:** **Video Visual Critic** (Gemini vision) reviews stills + video frames and talks to **Product Video Prompt Builder** through structured handoff text.

---

## Roles

| Agent / tool | Job |
|--------------|-----|
| **product-video-prompt-builder** | Writes Kling prompt from Module 4 image |
| **Kling render** | `factory_cli render` |
| **video-visual-critic** | Gemini scores clip, lists fixes, suggests revised prompt |
| **module1-qc-runner** | Hard compliance gate before upload (still required) |

Gemini is **not** a substitute for Module 1 QC — it helps you **iterate faster** before QC.

---

## Flow

```
Module 4 image
  → (optional) review-image — ready for Kling?
  → product-video-prompt-builder → prompt
  → factory_cli render
  → review-and-suggest — Gemini watches frames + reference still
  → if not good enough: handoff → prompt builder → regen (max 2–3)
  → pan loop + caption
  → module1-qc-runner
  → enqueue / post
```

---

## Commands

```bash
# Before first render
python3 -m shorts_bot.tiktok_shop.visual_feedback_cli review-image \
  --image data/tiktok_shop/images/PRODUCT.jpg --product "Name"

# After render
python3 -m shorts_bot.tiktok_shop.visual_feedback_cli review-and-suggest \
  --video data/tiktok_shop/clips/name_loop.mp4 \
  --reference-image data/tiktok_shop/images/PRODUCT.jpg \
  --product "Name" \
  --prompt "Arc Camera Shot from left to right..."

# Paste block for prompt builder
python3 -m shorts_bot.tiktok_shop.visual_feedback_cli handoff \
  --critique data/tiktok_shop/visual_feedback/video_name_loop.json
```

Reports: `data/tiktok_shop/visual_feedback/*.json`

---

## CEO orchestration

1. Dispatch **video-visual-critic** (background) after each Kling render  
2. If `good_enough=false`, dispatch **product-video-prompt-builder** with `handoff` output  
3. Re-render with new prompt — do not post until visual critic + Module 1 QC happy  

Slash: `/visual-review` · Subagent: `.cursor/agents/video-visual-critic.md`

---

## Secrets

**GEMINI_API_KEY** required (same as Module 1 vision QC).

Optional: **GEMINI_VISION_MODEL** — defaults to `gemini-2.5-flash` (smarter than lite for QC/critic; lite stays on scrape OCR via `GEMINI_MODEL`).
