# Laptop always on — daily videos without you remembering

You said you can leave the laptop running. **This is the best path** — no Cursor Automations needed.

---

## What this does

Laptop runs the bot 24/7. Every day at the time you pick, it automatically:

1. Picks the next AI product to review  
2. Starts InVideo  
3. Tries to generate + download the video  
4. Uploads to YouTube (if the MP4 exists)

**You do not need to open Cursor every day.**

---

## One-time setup (~20 minutes)

### 1. Get the code on your laptop

```bash
cd ~/proof-codex-ai   # or wherever you cloned it
git pull
bash scripts/install.sh
```

### 2. Tell the bot to run daily (edit `.env`)

Open the file `.env` in the project folder. Add or change these lines:

```env
PIPELINE_BACKEND=invideo
AUTO_DAILY_ENABLED=true
AUTO_DAILY_HOUR=17
AUTO_DAILY_MINUTE=0
AUTO_APPROVE_DRAFTS=true
AUTO_UPLOAD_YOUTUBE=true
YOUTUBE_UPLOAD_VISIBILITY=public
BROWSER_ENABLED=true
```

**Time is UTC.** Examples:

| You want (Pacific) | Set AUTO_DAILY_HOUR |
|--------------------|---------------------|
| 9:00 AM PT | 17 |
| 12:00 PM PT | 20 |
| 6:00 PM PT | 2 (next UTC day) |

Check time: `python3 -m src.clock`

### 3. Log into InVideo once (on the laptop)

```bash
python3 -m shorts_bot.invideo.handoff_cli
```

Use the **Desktop** browser tab → sign in with Google (or email).  
Check: `python3 -m shorts_bot.invideo.auth_cli status` → should say logged in.

### 4. YouTube login once (if not done)

```bash
python3 -m shorts_bot.youtube.auth_cli
```

### 5. Keep the bot running

```bash
bash scripts/run-all.sh
```

Leave that terminal open (or run in background — see below).  
Open **http://localhost:8080** anytime to see status.

### 6. Stop laptop from sleeping

**Mac:** System Settings → Battery → turn off sleep on power adapter, or plug in and leave lid open.

**Windows:** Settings → Power → “Never” sleep when plugged in.

---

## Test before trusting the timer

```bash
python3 -m shorts_bot.production.invideo_daily_cli
```

If it fails on **credits**, fix InVideo plan once — then daily runs work without you.

---

## Run in background (optional)

**Mac/Linux** — so you can close the terminal window:

```bash
cd ~/proof-codex-ai
nohup bash scripts/run-all.sh >> data/web.log 2>&1 &
```

Stop later: `bash scripts/stop.sh`

---

## If something breaks

Read: `data/ALERTS.md` on the laptop (or tell the cloud agent to read it).

Common fixes:

| Problem | Fix |
|---------|-----|
| InVideo credits | Upgrade InVideo or generate on laptop once |
| Not logged in | Run `handoff_cli` again |
| No MP4 | Paste Drive link to cloud agent → `fetch_url_cli` |

---

## You vs the bot

| You (once) | Bot (every day) |
|------------|-----------------|
| Leave laptop plugged in | Picks product |
| Run `run-all.sh` | InVideo + upload |
| InVideo credits / login | Logs failures to ALERTS.md |

You are **not** the daily alarm. The laptop is.

---

## Optional: Cursor `/loop` on the same machine

If you also keep **Cursor open** on the laptop, you can add:

```
/loop every 24h run daily ship
```

Backup only — **`run-all.sh` + AUTO_DAILY** is the main schedule.
