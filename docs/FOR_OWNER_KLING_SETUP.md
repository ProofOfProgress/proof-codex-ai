# Kling setup — TikTok Shop affiliate (official API)

**Model guide:** `docs/KLING_MODEL_GUIDE.md` — read this for which Kling version to use.

---

## What you need

| Secret | Purpose |
|--------|---------|
| `KLING_ACCESS_KEY` + `KLING_SECRET_KEY` | Official API (JWT) — **preferred** |
| or `KLING_API_KEY` | Single bearer key |
| `KLING_PROVIDER` | `official` |
| `KLING_MODEL` | `kling-v2-6` |
| `KLING_MODE` | `std` (720p, ~$0.21/5s) for launch |
| `KLING_CLIP_SECONDS` | `5` (course Module 5) |

After saving secrets → **new cloud agent run** → `bash scripts/install.sh`

---

## Verify

```bash
python3 -m shorts_bot.tiktok_shop status
python3 -m shorts_bot.tiktok_shop.factory_cli render --product "NAME" --image PATH/TO/module4.jpg --force
```

---

## Course alignment

- **Model:** Kling **2.6** (`kling-v2-6`)
- **Duration:** 5 seconds
- **Audio:** off
- **Prompt:** fixed arc-camera text in Module 5 (or Product Video Prompt Builder for custom sets)

---

## Dry run (no FastMoss yet)

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli render \
  --product "Your Product" \
  --image data/tiktok_shop/images/your_module4_image.jpg \
  --force
python3 -m shorts_bot.tiktok_shop.factory_cli qc \
  --video data/tiktok_shop/clips/your_product_final.mp4 \
  --product "Your Product" \
  --caption "..." \
  --account affiliate_main
```

Outputs: `data/tiktok_shop/clips/` (raw 5s → loop ~10s → final with caption)

---

## Billing

Add credits at https://klingai.com — without credits, render fails even with valid keys.

**Do not** use Replicate `kwaivgi/kling-v3-video` slug with the official API — the bot maps it to `kling-v2-6` automatically.
