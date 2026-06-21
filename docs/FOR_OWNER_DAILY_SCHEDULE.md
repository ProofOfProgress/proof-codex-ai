# Daily post — one prompt, runs on a schedule

You want: **tell the bot once → every day at a set time → make + post a Short.**

InVideo made the old “one-click daily” harder (credits, browser, MP4 handoff). This doc gives you **two ways** to schedule it — pick one.

---

## Recommended: Cursor Automations (cloud)

Works even when your laptop is off. The agent runs in the cloud on a timer.

### Setup (one time, ~5 minutes)

1. Open **https://cursor.com/automations**
2. Click **New automation**
3. **Name:** `Daily AI product Short`
4. **Trigger:** **Schedule (cron)**
   - Example: every day at **9:00 AM Pacific** → cron `0 17 * * *` (17:00 UTC = 9am PT)
   - [Cron helper](https://crontab.guru/) if you need another time
5. **Repository:** `ProofOfProgress/proof-codex-ai`
6. **Prompt:** copy everything from `data/DAILY_AUTOMATION_PROMPT.txt` in the repo (or below)
7. **Save** and turn it **On**

### Copy-paste prompt (daily post)

```
Repo: ProofOfProgress/proof-codex-ai

Run the InVideo daily ship — one AI product review Short:

python3 -m shorts_bot.production.invideo_daily_cli

Rules:
- InVideo is the soul of the channel — do not use old Blender/Recraft render.
- If InVideo credits block Generate: note in data/ALERTS.md and tell owner to paste a Google Drive link for that draft.
- If MP4 exists but upload skipped: run upload_canonical_cli for that draft.
- Max 1 YouTube upload per 24h (YPP_SAFE_MODE).
- Post a 5-line summary: product, draft #, project URL, YouTube link or what blocked.

Read docs/PRIORITIES.md — top 4 only.
```

That’s it. Same prompt every day. Change the cron if you want a different time.

---

## Option B: Bot runs daily while web UI is up

If the VM or home machine runs `python3 -m shorts_bot.web` 24/7:

In `.env`:

```env
PIPELINE_BACKEND=invideo
AUTO_DAILY_ENABLED=true
AUTO_DAILY_HOUR=17
AUTO_DAILY_MINUTE=0
AUTO_APPROVE_DRAFTS=true
AUTO_UPLOAD_YOUTUBE=true
YOUTUBE_UPLOAD_VISIBILITY=public
```

Times are **UTC**. Restart web UI after editing.

Manual test anytime:

```bash
python3 -m shorts_bot.production.invideo_daily_cli
```

---

## What one daily run does

| Step | Who |
|------|-----|
| Pick next AI product (ChatGPT Plus, NotebookLM, …) | Bot |
| Send brief to InVideo (master prompt + product) | Bot |
| Generate + download MP4 in browser | Bot (needs InVideo login + credits) |
| Upload to YouTube | Bot |
| Log failure to `data/ALERTS.md` | Bot |

---

## When InVideo blocks you (credits / login)

The daily run **won’t silently fail** — it writes to `data/ALERTS.md`.

**Your fallback (no file attach in Cursor):**

1. Open the project URL from the alert on your laptop  
2. Generate → Download  
3. Google Drive → share link → paste in chat  

Agent runs:

```bash
python3 -m shorts_bot.invideo.fetch_url_cli --draft-id N 'DRIVE_URL'
python3 -m shorts_bot.production.upload_canonical_cli --draft-id N --video data/production/draft_N/final_short.mp4
```

---

## Change the time

- **Cursor Automation:** edit the cron on [cursor.com/automations](https://cursor.com/automations)  
- **Web UI:** change `AUTO_DAILY_HOUR` / `AUTO_DAILY_MINUTE` in `.env` (UTC)

---

## One-liner you can say in chat anytime

> **“Run daily ship”**

Same as `python3 -m shorts_bot.production.invideo_daily_cli`.
