# Kling model guide — TikTok Shop affiliate clips

**Course default:** **Kling 2.6** · 5 seconds · audio off · arc-camera prompt (`module_05_ai_video_generation.md`)

**Bot default (official API):** `kling-v2-6` · `mode=std` · 5s · `sound=off`

---

## Which model to use

| Model | API `model_name` | Use for affiliate? | Notes |
|-------|------------------|--------------------|-------|
| **Kling 2.6** | `kling-v2-6` | **Yes — primary** | Course instructor default. Best balance of motion quality + Module 1 compliance when paired with arc prompt. Supports `sound=off`. |
| Kling 2.5 Turbo | `kling-v2-5-turbo` | Backup only | Faster/cheaper; test if 2.6 regens fail QC. Not the course default. |
| Kling 2.1 / 2.1 Master | `kling-v2-1`, `kling-v2-1-master` | No | Older; worse product fidelity vs 2.6. |
| Kling 2.0 Master | `kling-v2-master` | No | Legacy. |
| Kling 1.x | `kling-v1`, `kling-v1-5`, `kling-v1-6` | No | Deprecated for Shop clips. |
| Kling 3.0 | `kling-v3` | Experiment later | Course mentions as optional; Higgsfield label. Official API support varies by account tier — **do not switch launch batch to v3** until dry-run QC passes. |
| Replicate `kwaivgi/kling-v3-video` | N/A on official API | **Wrong backend** | Replicate slug — **not** valid on `api.klingai.com`. Bot auto-maps to `kling-v2-6` when `KLING_PROVIDER=official`. |

---

## std vs pro (mode)

| Mode | Resolution | Cost (typical) | When |
|------|------------|----------------|------|
| **`std`** | 720p | ~**$0.21 / 5s** clip | **Launch + daily ops** — budget plan in `LAUNCH_BUDGET.md` |
| **`pro`** | 1080p | Higher | After revenue justifies it; course Higgsfield path often outputs 1080p but **cost matters at 8–10/day** |

Set in Cursor Secrets: `KLING_MODE=std` (Environment Variable).

---

## Duration

| Setting | Affiliate |
|---------|-----------|
| **5 seconds** | **Yes** — course + `render.py` hardcoded for Shop pipeline |
| 10 seconds | Not used for affiliate (bubble / legacy peripheral config used 10–15s) |

Pan loop doubles 5s → ~10s final (`video_variants.make_pan_loop_clip`).

---

## Audio

| Setting | Affiliate |
|---------|-----------|
| **`sound=off`** | **Yes** — course Module 5; bot forces off in `render.py` |
| `KLING_GENERATE_AUDIO=true` in `.env` | Legacy peripheral config — **ignore for Shop** |

---

## Provider

| Provider | Secret | Shop affiliate |
|----------|--------|----------------|
| **Official** | `KLING_API_KEY` or `KLING_ACCESS_KEY` + `KLING_SECRET_KEY` | **Use this** — `KLING_PROVIDER=official` |
| Replicate | `REPLICATE_API_TOKEN` + `kwaivgi/kling-v3-video` | Not wired to Shop factory today |

---

## Recommended Cursor Secrets (affiliate launch)

| Secret | Value |
|--------|--------|
| `KLING_PROVIDER` | `official` |
| `KLING_MODEL` | `kling-v2-6` |
| `KLING_MODE` | `std` |
| `KLING_CLIP_SECONDS` | `5` |
| `KLING_GENERATE_AUDIO` | `false` |
| `KLING_ASPECT_RATIO` | `9:16` |

After changing secrets → **new cloud agent run** → `bash scripts/install.sh`.

---

## Prompt (do not change for launch)

```
Arc Camera Shot from left to right, handheld but naturally stabilized. Motion is smooth and organic with gentle human drift, not shaky. Keep all of the products stationary and in the center of the shot.
```

Source: course Module 5 · `render.ARC_CAMERA_PROMPT` · delegate rewrites to `product-video-prompt-builder` only when image needs custom set dressing.

---

## References

- Official API: https://app.klingai.com/global/dev/document-api/apiReference/model/imageToVideo
- Course: `data/research/course/module_05_ai_video_generation.md`
- Owner setup: `docs/FOR_OWNER_KLING_SETUP.md` *(needs refresh for official API — see this doc)*
