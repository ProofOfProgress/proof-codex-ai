---
name: team
description: Show the agent team roster, how to talk to each employee, and latest mission status. Use when the owner wants to see who's available, watch CEO activity, or check parallel work.
---

# /team — your agent employees

## Roster

| Employee | Slash | Job | Background? |
|----------|-------|-----|-------------|
| **Affiliate CEO** | `/affiliate-ceo` | Orchestrates pipeline, delegates in parallel | No |
| **Product Video Prompt Builder** | `/product-video-prompt-builder` | Module 5 Kling/Higgsfield **video prompts** | No |
| **Video Caption Writer** | `/video-caption-writer` | Module 6 on-screen caption copy | No |
| **Video Editor** | `/video-editor` | Pan loop + caption burn (~10s finish) | **Yes** |
| **Module 1 QC Runner** | `/module1-qc-runner` | Pre-upload violation check | **Yes** |

## Talk to any employee directly

Type the slash command + your request. Attach files when needed (product image for prompt builder, MP4 path for QC).

Examples:

```
/product-video-prompt-builder
(write TikTok 9:16 UGC video prompt — attach product image)

/video-caption-writer
Pain-point caption for a car phone mount

/video-editor
Loop and burn caption on data/tiktok_shop/renders/raw.mp4 — caption: "Your hook text here" — output: data/tiktok_shop/renders/final.mp4

/module1-qc-runner
QC this file: data/tiktok_shop/renders/foo.mp4 product "Car mount"

/affiliate-ceo
Make a clip for this product — coordinate the team
```

## Watch CEO ↔ employee workflow

Every orchestrated run writes a **mission log** you can inspect:

```bash
python3 -m shorts_bot.agent_ops missions          # list recent missions
python3 -m shorts_bot.agent_ops tail --mission latest   # live event feed
python3 -m shorts_bot.agent_ops status --mission latest # summary
```

**Web dashboard** (auto-refreshes):

```bash
python3 -m shorts_bot.web
```

Open: http://127.0.0.1:8080/agent-ops

## What gets logged

- `mission_created` — new pipeline run
- `dispatch_background` / `dispatch_foreground` — CEO sends work to an employee
- `started` / `completed` / `failed` — employee progress
- `owner_message` — you talked to an employee directly (when logged)

Full guide: `docs/FOR_OWNER_AGENT_TEAM.md`
