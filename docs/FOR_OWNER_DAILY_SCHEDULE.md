# Daily post — what actually works

Cursor **Automations** at cursor.com/automations do **not** work for everyone (plan, repo, or UI bugs). Skip them if you already tried.

---

## Plan A — One message when you’re in Cursor (works today)

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
