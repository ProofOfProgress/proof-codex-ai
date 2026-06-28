---
name: affiliate-make-clip
description: End-to-end affiliate clip — scout optional, Kling std render, pan loop, Module 6 caption burn, Module 1 QC. Use when Isaac asks to make a Shop video without hand-holding every CLI step.
---

# Affiliate make-clip (factory path)

**Execution lives on the VM** via CLI — not in chat imagination. Git commits are handoff, not the runtime.

## When to use

- "Make a clip for [product]"
- Private test on @gspgsgsorip1 (`affiliate_test`)
- After scout picked a product

## Course (creative)

| Step | Source |
|------|--------|
| Product pick | `module_03_product_research_strategies.md` |
| Image | `PROMPT_BUILDER.md` → `factory_cli gen-image` or owner image |
| Kling motion | Fixed arc-camera — `module_05_ai_video_generation.md` |
| Caption burn | `module_06_editing.md` — white box / black text (automated in pipeline) |

## Commands

```bash
# Optional scout first
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 10

# Full pipeline (render + loop + caption + queue)
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "PRODUCT_NAME"

# QC only
python3 -m shorts_bot.tiktok_shop.factory_cli qc --video data/tiktok_shop/clips/..._final.mp4 \
  --product "PRODUCT_NAME" --caption "..." --account affiliate_test

# Private post (one-off env — no secrets edit)
ZERNIO_TIKTOK_PRIVACY=SELF_ONLY python3 -m shorts_bot.tiktok_shop.factory_cli post --account affiliate_test --confirm
```

## Subagents (scale)

Use `/affiliate-ceo` — delegates to `video-editor`, `module1-qc-runner`, and other specialists. See `docs/FOR_OWNER_AGENT_TEAM.md`.

## Secrets (Cloud Agent → new run after change)

`KLING_ACCESS_KEY`, `KLING_SECRET_KEY`, `KLING_MODE=std`, `KLING_MODEL=kling-v2-6`, `GEMINI_API_KEY`, `ZERNIO_API_TOKEN`

## Account note

`affiliate_test` and `bubble_playstation` are the same TikTok (@gspgsgsorip1). Old handle: playstationaccou2171.
