# Prompt builder (owner override)

**We do NOT use** the course’s NanoBanana Pro Auto Prompter Google Sheet.

**We USE** the **Product Video Prompt Builder** for **AI video prompts** — same instructions as the course community ChatGPT:

https://chatgpt.com/g/g-69ba84bb288481919efbb9d1b7aad690-product-video-prompt-builder

This is **not** an image prompt tool. It writes **video-generation prompts** (Kling / Higgsfield) from an uploaded product image.

## Cursor subagent (preferred in this repo)

Full instructions live in `.cursor/agents/product-video-prompt-builder.md`.

| How | Command |
|-----|---------|
| Invoke directly | `/product-video-prompt-builder` — attach the Module 4 product image |
| Natural language | "Use the product video prompt builder to write a Kling video prompt for this image" |

The subagent outputs **one paragraph of video prompt text only**, ready to paste into Higgsfield → Video → Kling 2.6.

## Workflow (Module 5)

1. Finish the **Module 4 product image** (isolated product, 9:16, 2K).
2. Attach that image to **Product Video Prompt Builder** (Cursor subagent or ChatGPT link).
3. Copy the output into **Higgsfield → Video → Create Video** (Kling 2.6, GENERAL, 5s, audio off, enhance off).
4. Generate the clip, then edit per Module 6. Run **Module 1 QC** before any upload.

## Bot wiring

GPT **Instructions** are saved in `.cursor/agents/product-video-prompt-builder.md`. When owner adds **example prompts** (product image in → video prompt out), append them below and encode in `shorts_bot/tiktok_shop/` prompt builder — **do not** use the Google Sheet.

## Image terms (input to the builder)

The builder needs the **product image** as visual reference — not a new image prompt.

- **Product image** — isolated product, blank/white background (from Module 4)
- **Reference image** — optional; product in a natural setting (for scale context when the builder needs it)
