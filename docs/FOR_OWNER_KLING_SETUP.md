# Kling setup — for the owner (plain English)

Kling runs through **Replicate**. You already have a Replicate token on this agent. One switch was missing — **turn generation on**.

---

## Step 1 — Cursor Secrets (do this once)

Open **Cursor → your Cloud Agent → Secrets** and add or fix these:

| Secret name | Set to |
|-------------|--------|
| `REPLICATE_API_TOKEN` | Your token from https://replicate.com/account/api-tokens (starts with `r8_`) — **you likely have this already** |
| `AI_VIDEO_GENERATION_ENABLED` | `true` |
| `VIDEO_BACKEND` | `kling` |
| `VISUAL_STYLE` | `ai_video` |

Optional (defaults are fine):

| Secret name | Default |
|-------------|---------|
| `KLING_MODEL` | `kwaivgi/kling-v3-video` |
| `KLING_CLIP_SECONDS` | `15` |
| `KLING_CLIPS_PER_SHORT` | `2` |

---

## Step 2 — Replicate billing

Kling costs money per run (~2 calls per Short).

1. Go to https://replicate.com/account/billing  
2. Add a payment method or credits  
3. Without billing, generations fail even with a valid token

---

## Step 3 — Sync on the agent

After saving secrets, start a **new agent run** (or tell the agent):

```bash
bash scripts/install.sh
python3 -m shorts_bot.production.kling_setup_cli
```

You want all rows **OK** in green.

---

## Step 4 — Test one Short (no upload)

```bash
python3 -m shorts_bot.production.daily_cli --topic "village eye dream" --no-upload
```

When it finishes, open the video file it prints (under `data/production/draft_N/final_short.mp4`) and watch locally before posting.

---

## What Kling does for PERIPHERAL

- **2 clips × 15 seconds** → ~30s Short, **one stitch**
- **Character voices in the video** (lip sync) — no narrator robot voice
- **Subtitles** still added after (burned in)
- **Horror sound effects** layered on top at the end

---

## If something fails

| Error | Fix |
|-------|-----|
| "AI video generation is disabled" | Set `AI_VIDEO_GENERATION_ENABLED=true` in Secrets |
| "Kling requires REPLICATE_API_TOKEN" | Add token in Secrets, re-run install |
| Replicate 402 / payment | Add billing at replicate.com |
| Generation timeout | Normal — each clip can take several minutes; agent runs in background |

Full technical doc: `docs/KLING_VIDEO_PIPELINE.md`
