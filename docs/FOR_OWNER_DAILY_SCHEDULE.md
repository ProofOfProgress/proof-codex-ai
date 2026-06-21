# Daily post — what actually works

Cursor **Automations** at cursor.com/automations do **not** work for everyone — skip if you already tried.

---

## Best path: laptop always on (recommended for you)

You said you can leave the laptop running. **Use this.**

Full guide: **`docs/FOR_OWNER_LAPTOP_ALWAYS_ON.md`**

Short version:

1. `git pull` + `bash scripts/install.sh`
2. In `.env`: `AUTO_DAILY_ENABLED=true` + pick `AUTO_DAILY_HOUR` (UTC)
3. `python3 -m shorts_bot.invideo.handoff_cli` (login once)
4. `bash scripts/run-all.sh` — leave it running, laptop plugged in, no sleep

The bot fires **daily ship** by itself. You don't open Cursor every day.

Test once: `python3 -m shorts_bot.production.invideo_daily_cli`

---

Open Cursor → chat → type:

**`daily ship`**

Same as running the full daily pipeline (pick product → InVideo → upload if MP4 exists).

Do this once a day when you can. Set a **phone alarm** or calendar reminder: *“Message Cursor: daily ship”* — that’s your schedule.

---

## Plan B — Slack (if you use #peripheral-ops)

With web UI running and Slack connected:

```
@cursor agent run daily ship on proof-codex-ai
```

Or post in ops channel if autonomy is wired.

---

## Plan C — Home PC always on (advanced)

If your home machine runs the bot 24/7, see `docs/RUN_AT_HOME.md` and in `.env`:

```env
PIPELINE_BACKEND=invideo
AUTO_DAILY_ENABLED=true
AUTO_DAILY_HOUR=17
AUTO_DAILY_MINUTE=0
```

Then `python3 -m shorts_bot.web` stays running — bot fires daily internally. **Not for the cloud VM** (no cron there).

---

## What blocks fully hands-off daily

| Blocker | Fix |
|---------|-----|
| InVideo credits | Upgrade or generate on laptop |
| No MP4 | Drive link → paste in chat |
| Automations broken | Use Plan A (phone reminder) |

---

## First priority before daily habit

**Ship one video:** laptop InVideo → Download → Drive link → paste here → I upload.

Daily schedule only matters after one full loop works.
