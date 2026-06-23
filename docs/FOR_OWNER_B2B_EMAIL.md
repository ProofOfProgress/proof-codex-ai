# Hook up your business email (B2B outreach)

**What this does:** Lets the bot send **B2B sales emails** from **your** Google / Gmail address — same login you use for Slack alerts.

**Safety:** Sending is **off** until you flip one switch. Max **10 emails per day**. Every send needs `--confirm`.

---

## One-time setup (~5 min)

### 1. Use your business Gmail / Google Workspace

Example: `you@rapidtoolreview.com` or your ops Gmail.

You need **2-Step Verification** on that Google account.

### 2. Create an App Password

1. Open [Google Account → Security](https://myaccount.google.com/security)
2. Turn on **2-Step Verification** if it is not already
3. Search **App passwords** (or Security → App passwords)
4. Create one named e.g. `Rapid Tool Review B2B`
5. Copy the **16-character** password (spaces are fine)

This is **not** your normal Gmail password.

### 3. Add Cursor Secrets

In **Cursor → your cloud agent → Secrets**, add or update:

| Secret | What to put |
|--------|-------------|
| `GMAIL_SMTP_USER` | Your business email address |
| `GMAIL_SMTP_APP_PASSWORD` | The 16-char app password |
| `B2B_EMAIL_ENABLED` | `true` (only after you are ready to send) |
| `B2B_EMAIL_FROM_NAME` | Your first name, e.g. `Kim` |

Then on the VM:

```bash
bash scripts/install.sh
python3 -m shorts_bot.b2b.outreach_cli status
```

You should see **SMTP configured: yes**.

### 4. Send yourself a test

```bash
python3 -m shorts_bot.b2b.outreach_cli test-email
```

Check your inbox for `[Rapid Tool Review] B2B email test`.

---

## Daily workflow

**1. Draft + save a prospect**

```bash
python3 -m shorts_bot.b2b.outreach_cli save \
  --company "SomeStartup" \
  --product "SomeTool" \
  --detail "Product Hunt launch Tuesday" \
  --channel email \
  --contact "founder@startup.com"
```

**2. Read the draft** — tweak one line so it sounds like you.

**3. Send (only when ready)**

```bash
python3 -m shorts_bot.b2b.outreach_cli send --index 0 --confirm
```

`--index` is the row number in `data/b2b/prospects.json` (shown when you `save`).

---

## Commands cheat sheet

| Command | Purpose |
|---------|---------|
| `outreach_cli status` | Is email wired? How many sent today? |
| `outreach_cli test-email` | Ping yourself |
| `outreach_cli draft ... --channel email` | Preview one email |
| `outreach_cli save ... --contact email@...` | Save to prospect list |
| `outreach_cli send --index N --confirm` | Actually send |

Send log: `data/b2b/send_log.jsonl`

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Business email not configured` | Set `GMAIL_SMTP_USER` + `GMAIL_SMTP_APP_PASSWORD` in Secrets → `bash scripts/install.sh` |
| `Gmail auth failed` | Use an **App Password**, not your login password |
| `B2B email disabled` | Set `B2B_EMAIL_ENABLED=true` in Secrets |
| `Daily limit reached` | Wait until tomorrow (UTC) or ask agent to raise `B2B_EMAIL_DAILY_LIMIT` |
| Email lands in spam | Normal for new outreach — warm up slowly, tweak copy, use your real name |

---

## Same keys as Slack email

If you already set up Slack alerts via Gmail (`docs/FOR_OWNER_SLACK_EMAIL.md`), you only need to add:

- `B2B_EMAIL_ENABLED=true`
- `B2B_EMAIL_FROM_NAME=Kim` (your name)

The bot uses the same Gmail SMTP login for both Slack alerts and B2B outreach.
