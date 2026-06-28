---
name: pre-publish-gate
description: Run mandatory pre-publish checks before any TikTok/Zernio upload. Use when posting videos, bubble wrap carousels, or batch uploads. Prefer Python gate (cheap) over re-reading course in chat.
---

# Pre-publish gate

**Do not upload** until the gate passes. This saves Cursor compute — run checks in Python, not by re-analyzing video in chat.

## Commands

**Bubble wrap carousel (2 PNGs):**

```bash
python3 scripts/pre_publish_gate.py --type carousel --tier fast \
  --slide1 PATH/slide1_hook.png --slide2 PATH/slide2_cta.png \
  --title "..." --account bubble_proof
```

**Affiliate video:**

```bash
python3 scripts/pre_publish_gate.py --type video --tier standard \
  --video PATH/clip.mp4 --caption "..." --product "NAME" --account bubble_isaac
```

**Factory CLI (same checks):**

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli qc --video PATH --product NAME --caption "..."
```

## Tiers (compute cost)

| Tier | What runs | When to use |
|------|-----------|-------------|
| `fast` | Caption bans, posting spacing, file format, AIGC config — **no Gemini vision** | Daily bubble wrap batches |
| `standard` | fast + vision QC when `MODULE1_VISION_QC_ENABLED=true` | Affiliate clips before first post |
| `full` | Same as standard today | Alias for standard |

Set default: `PRE_PUBLISH_DEFAULT_TIER=fast` in env for cheapest daily ops.

## Code path

Upload functions call `run_pre_publish_gate` automatically — `post_clip`, `post_bubble_wrap_carousel`.

## Owner tips

Rules live in `data/operating_tips.json`. List: `python3 -m shorts_bot.operating.tips_cli list`

Agent checklist (no LLM): `python3 -m shorts_bot.operating.tips_cli checklist`
