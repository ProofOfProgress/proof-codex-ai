# /loop — daily video without remembering

Use Cursor’s **`/loop`** on your **laptop** (repo open, Cursor stays running).  
You are **not** giving the cloud agent access to your laptop — the **local** Cursor agent runs on a timer.

---

## Before you start (once)

On the **same laptop** where Cursor will stay open:

```bash
cd ~/proof-codex-ai   # your project folder
git pull
bash scripts/install.sh
python3 -m shorts_bot.invideo.handoff_cli    # InVideo login once
python3 -m shorts_bot.invideo.auth_cli status   # should say logged in
python3 -m playwright install chromium
```

Test manually once:

```bash
python3 -m shorts_bot.production.invideo_daily_cli
```

If **credits** block you, fix InVideo plan once — loop will hit the same wall until then.

---

## Turn on /loop (copy-paste)

1. Open **Cursor** on your laptop (not cloud-only chat).
2. Open the **proof-codex-ai** folder as the project.
3. Open **Agent** chat (side panel).
4. Paste **one** of these and send:

### Every 24 hours (recommended)

```
/loop every 24h --max-turns 3 --max-runtime 45m

Run daily ship for this repo:
python3 -m shorts_bot.production.invideo_daily_cli

Rules:
- InVideo is the soul of the channel — no Blender/Recraft render.
- If credits block: append to data/ALERTS.md with draft # and project URL; stop (do not spin forever).
- If MP4 exists but upload failed: python3 -m shorts_bot.production.upload_canonical_cli --draft-id N --video data/production/draft_N/final_short.mp4
- Max 1 YouTube upload per 24h.
- Reply in 5 lines: product, draft #, YouTube URL or blocker.
```

### Same time every day at 9am Pacific (if your Cursor supports cron-style /loop)

```
/loop cron "0 17 * * *" --max-turns 3 --max-runtime 45m

(same prompt body as above — daily ship + rules)
```

`17:00 UTC` ≈ 9:00 AM Pacific (DST varies — check with `python3 -m src.clock`).

---

## Keep it alive

| Do | Why |
|----|-----|
| Laptop **plugged in** | Power |
| **Sleep off** when plugged in | Loop stops if machine sleeps |
| **Cursor open** | /loop is tied to Cursor session |
| **Don’t quit Cursor** | Closing Cursor stops the loop |

Optional: prevent Mac sleep while plugged in — System Settings → Battery.

---

## How you know it worked

- Next day: new line in `data/ALERTS.md` if something failed  
- Or new draft folder `data/production/draft_N/` with `invideo_project.url`  
- Or YouTube upload — agent’s 5-line summary in chat  

---

## If /loop never fires again

Known Cursor bug: **long intervals (24h) sometimes die silently.** Fixes:

1. Try shorter test first: `/loop every 30m` with `--max-turns 1` and a tiny task — see if it ticks once.  
2. Fallback: `.env` + `bash scripts/run-all.sh` — see `docs/FOR_OWNER_LAPTOP_ALWAYS_ON.md`  
3. Tell cloud agent: “/loop didn’t tick” — we debug.

---

## Cloud vs laptop

| | **/loop on laptop** | **Cloud agent chat** |
|---|---------------------|----------------------|
| Sees your InVideo login | ✅ (local browser profile) | Separate cloud profile |
| Needs Cursor open on laptop | ✅ | ❌ |
| Good for daily ship | ✅ **best for InVideo** | OK for code, weaker for InVideo browser |

---

## One-line reminder

Laptop + Cursor open + `/loop every 24h` + daily ship prompt = **you are not the alarm clock.**
