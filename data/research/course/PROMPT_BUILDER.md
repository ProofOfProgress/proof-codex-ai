# Prompt builder (owner override)

## Module 4 — Gemini sample first (owner pipeline tip)

Put the **listing product photo** into **Gemini** → get a **full-bleed 9:16 sample** (whole product visible, staged background) → feed **that sample** to Kling + prompt-builder video prompt.

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli sample-image \
  --product "Car Phone Mount" --source listing.jpg [--reference ref.jpg]
```

Output: `data/tiktok_shop/samples/car_phone_mount_916.jpg` · model `gemini-2.5-flash-image`

**We do NOT use** the course's NanoBanana Pro Auto Prompter Google Sheet.

**We USE** the **Product Video Prompt Builder** for **AI video prompts** — same instructions as the course community ChatGPT:

https://chatgpt.com/g/g-69ba84bb288481919efbb9d1b7aad690-product-video-prompt-builder

This is **not** an image prompt tool. It writes **Module-1-compliant video-generation prompts** (Kling / Higgsfield) from an uploaded product image — see `module_01_read_before_anything.md` ban list.

## Cursor subagent (preferred in this repo)

Full instructions: `.cursor/agents/product-video-prompt-builder.md`

| How | Command |
|-----|---------|
| Direct | `/product-video-prompt-builder` — attach Module 4 product image |
| Via CEO | Ask the main agent to coordinate prompt + caption + edit + QC |
| Roster | `/team` |

Output: **one paragraph of video prompt text only**, ready for Higgsfield → Video → Kling 2.6.

## Workflow (Module 5)

1. Finish **Module 4 product image** (isolated product, 9:16, 2K).
2. Attach image → **Product Video Prompt Builder** (subagent or ChatGPT).
3. Paste output into **Higgsfield → Video → Kling 2.6** (GENERAL, 5s, audio off, enhance off).
4. CEO can run **Module 1 QC** in background while caption work continues — see `docs/FOR_OWNER_AGENT_TEAM.md`.
5. Module 1 QC before upload.

## Still-frame violations (official coach — 2026-06-29)

TikTok may flag **still frame** even when Kling motion looks “fine.” Coach law:

- **~25% more side-to-side** lateral camera travel in the **video prompt**
- **Micro-shake** + **background parallax** (decor shifts vs fixed product)
- Module 6 **post** adds lateral boost + micro-shake in `make_pan_loop_clip` automatically
- Module 1 QC now checks inter-frame motion — low motion **blocks upload**

Regenerate prompt via **product-video-prompt-builder**, re-render, re-loop — do not repost old MP4.

## Bot wiring

Instructions saved in `.cursor/agents/product-video-prompt-builder.md`. Example prompts (image in → video prompt out) append below; encode in `shorts_bot/tiktok_shop/` when ready.

## Image terms (input to the builder)

- **Product image** — Module 4 **staged 9:16 still** (complex background — NOT plain white listing box)
- **Reference image** — optional; product in setting for **scale** (leftmost when both attached)

CEO dispatch (attach both paths to subagent):

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli prompt-dispatch \
  --product "Insulated Tumbler" \
  --product-image data/tiktok_shop/images/MODULE4.jpg \
  --reference-image data/tiktok_shop/images/REF.jpg
```

Save subagent output:

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli save-prompt --product "NAME" --prompt "..."
```
