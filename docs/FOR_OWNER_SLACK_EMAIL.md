# Option A — Gmail into Slack (no bot token)

Post pipeline alerts to `#peripheral-ops` by **emailing the channel**. No `xoxb` bot token, no `/invite @cursor`, no Incoming Webhook.

**Catch:** Messages show as **email** in Slack (from your Gmail), not a polished bot avatar. Great for alerts and milestones — not for two-way agent chat or `[autonomy]` self-talk (that still needs Socket Mode + bot token).

---

## One-time setup (~5 min)

### 1. Get the channel email address

1. Open `#peripheral-ops` in Slack
2. Click the channel name → **Integrations** → **Email**
3. Copy the address — looks like `peripheral-ops@yourworkspace.slack.com`

### 2. Gmail App Password

Use the channel Google account (`paypalacc4progress@gmail.com` or your ops Gmail):

1. Google Account → **Security** → **2-Step Verification** (must be on)
2. **App passwords** → create one named e.g. `Peripheral Slack`
3. Copy the 16-character password (spaces optional)

### 3. Cursor Secrets

| Secret | Example |
|--------|---------|
| `SLACK_CHANNEL_EMAIL` | `peripheral-ops@yourworkspace.slack.com` |
| `GMAIL_SMTP_USER` | `paypalacc4progress@gmail.com` |
| `GMAIL_SMTP_APP_PASSWORD` | `abcd efgh ijkl mnop` |
| `SLACK_POST_MODE` | `email` (optional — force email-only; default `auto` tries bot/webhook first) |

```bash
bash scripts/install.sh
python3 -m shorts_bot.integrations test
```

You should see an **email** in `#peripheral-ops` from your Gmail with subject like `[Peripheral][setup] …`.

---

## What the bot sends

- Pipeline alerts (`auto_daily` failures, render errors)
- Test message on `integrations test`
- Web UI **Send test message** on Slack tab
- Anything that calls `post_slack_message()` / `notify_automation_alert()`

Subject line = short summary. Body = full text.

---

## When to use what

| Method | Outbound alerts | Two-way / threads | Setup difficulty |
|--------|-----------------|-------------------|------------------|
| **Email (Option A)** | Yes | No | Easiest |
| Incoming webhook | Yes | No | Easy |
| AlphaBeta001 bot token | Yes | Yes (with Socket Mode) | Medium |
| @cursor | Start Cloud Agents | Yes | OAuth + permissions |

**Recommended path if `/invite @cursor` fails:** Option A email for alerts + `@cursor` in DM once Link Account works.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Gmail auth failed | Use **App Password**, not your normal Gmail password |
| Nothing in Slack | Confirm `SLACK_CHANNEL_EMAIL` matches Integrations → Email exactly |
| Still asks for bot token | Set `SLACK_POST_MODE=email` and re-run `install.sh` |
| Message looks ugly | Expected — email format. Upgrade to bot token later if you want polish |

---

## Security

- App password is scoped — revoke in Google Account if leaked
- Channel email is workspace-specific — don’t publish it publicly
- Email is **outbound only** — agents cannot read Slack replies through this path
