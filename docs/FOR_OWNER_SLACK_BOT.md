# AlphaBeta001 — your own Slack bot (separate from @cursor)

**@cursor** is Cursor’s app — it only works when **you** link your Cursor account. It is not a separate “agent account.”

**AlphaBeta001 bot** is **your** Slack app — a real bot user in `#peripheral-ops` that posts pipeline alerts, subscriber milestones, and briefings. You control the name and icon.

Use **both** if you can: bot = notifications; @cursor = start coding agents from phone (when Link Account works).

---

## Create the bot (~15 min, one time)

### 1. Create a Slack app

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. Name: **AlphaBeta001** (or **Peripheral Ops**)
3. Pick your workspace → **Create App**

### 2. Bot permissions

1. Left menu → **OAuth & Permissions**
2. Under **Bot Token Scopes**, add:
   - `chat:write` — post messages
   - `chat:write.public` — post to public channels without joining (optional but helpful)
3. Scroll up → **Install to Workspace** → **Allow**
4. Copy **Bot User OAuth Token** (starts with `xoxb-`)

### 3. Add bot to your channel

1. Open `#peripheral-ops` in Slack
2. Channel name → **Integrations** → **Add an app** → choose **AlphaBeta001**
3. Or: in the channel type `@AlphaBeta001` and invite when prompted

### 4. Channel ID (for the bot to know where to post)

1. Open `#peripheral-ops`
2. Click channel name → scroll down — **Channel ID** starts with `C` (or right-click channel → Copy link — ID is in the URL)

### 5. Cursor Secrets

Add to **Cursor → Secrets** (not chat):

| Secret | Example |
|--------|---------|
| `SLACK_BOT_TOKEN` | `xoxb-...` |
| `SLACK_CHANNEL_ID` | `C0123456789` |

Optional: keep `SLACK_WEBHOOK_URL` too — bot token is preferred when set.

Then:

```bash
bash scripts/install.sh
python3 -m shorts_bot.integrations test
```

You should see a message from **AlphaBeta001** (your bot), not from a generic webhook name.

---

## Icon (optional)

Slack app → **Basic Information** → **Display Information** → upload eye logo from `channel/brand/assets/`.

---

## What the bot does (today)

- Posts test message on `integrations test`
- Posts pipeline alerts from `data/ALERTS.md` path (auto_daily failures, etc.)
- Does **not** replace @cursor for starting Cloud Agents — that’s still Cursor’s app + Link Account

---

## @cursor still broken?

Adding Cursor to the channel is not enough. You must:

1. Open **DM with Cursor** (Apps → Cursor) — not only the channel
2. `@cursor help` → **Link Account** (OAuth)
3. [Dashboard](https://cursor.com/dashboard?tab=integrations) → Cloud Agents enabled + usage pricing on
4. In channel, pick **@cursor** from autocomplete (the app) — then type your message

If Link Account never appears → workspace owner may need to approve Cursor, or your Cursor plan may not include Cloud Agents.

Contact Cursor support from `@cursor help` with **View request ID** if it still fails after Link Account.
