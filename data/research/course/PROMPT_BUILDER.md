# Prompt builder (owner override)

**We do NOT use** the course’s NanoBanana Pro Auto Prompter Google Sheet.

**We USE** the **Product Video Prompt Builder** — same instructions as the course community ChatGPT:

https://chatgpt.com/g/g-69ba84bb288481919efbb9d1b7aad690-product-video-prompt-builder

## Cursor subagent (preferred in this repo)

Full instructions live in `.cursor/agents/product-video-prompt-builder.md`.

| How | Command |
|-----|---------|
| Invoke directly | `/product-video-prompt-builder` then describe the product or attach an image |
| Natural language | "Use the product video prompt builder to write a UGC prompt for this image" |

The subagent outputs **prompt text only** (one paragraph, production-ready for Higgsfield/Kling). Attach the product image when you have it.

## Workflow

1. Run product + reference images through **Product Video Prompt Builder** (Cursor subagent above, or ChatGPT link).
2. Use the GPT output as the prompt for image/video generation (Higgsfield / Kling per module).
3. Still follow Module 1 QC before any upload.

## Video prompt (Module 5 — separate from GPT)

After the image is ready, video generation uses a **fixed all-purpose prompt** in Higgsfield/Kling 2.6 — see `module_05_ai_video_generation.md`. Do not run that through the ChatGPT builder.

## Bot wiring

GPT **Instructions** are saved in `.cursor/agents/product-video-prompt-builder.md`. When owner adds **example prompts** (product in → prompt out), append them below and encode in `shorts_bot/tiktok_shop/` prompt builder — **do not** use the Google Sheet.

## Image terms (from Module 4)

- **Product image** — isolated product, blank/white background  
- **Reference image** — product in a natural setting (for correct scale)
