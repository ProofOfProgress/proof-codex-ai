# B2B outreach email — separate inbox for AlphaBeta

**What this is:** A **dedicated outreach Gmail** for sales emails — **not** your personal email, **not** the old PayPal ops Gmail (that one stays for Slack/API alerts only).

**Who sends:** AlphaBeta drafts; **you** approve with `--confirm` before anything goes out.

**Safety:** Off until you enable it. Max **10 emails/day**. Every real send needs `--confirm`.

---

## Three emails — keep them separate

| Inbox | Used for | Touch it? |
|-------|----------|-----------|
| **PayPal ops Gmail** (`GMAIL_SMTP_*`) | Slack alerts, APIs, AlphaBeta ops | **No** — leave alone |
| **Your personal business email** | You, manually | Bot does **not** send from this |
| **New outreach inbox** (`B2B_SMTP_*`) | B2B cold email to startups | **Create this** |

---

## One-time setup (~10 min)

### 1. Create a new Gmail (or Google Workspace alias)

Pick a clean name, for example:

- `outreach@rapidtoolreview.com` (Workspace — best)
- `rapidtoolreview.outreach@gmail.com` (free Gmail — fine to start)

**Do not** reuse the PayPal ops account.

Turn on **2-Step Verification** on the new account.

### 2. App password for the outreach inbox

1. [Google Account → Security](https://myaccount.google.com/security) (signed into the **new** outreach account)
2. **App passwords** → create one named `RTR B2B Outreach`
3. Copy the 16-character password

### 3. Cursor Secrets

Add these — **separate from** `GMAIL_SMTP_*`:

| Secret | Example |
|--------|---------|
| `B2B_SMTP_USER` | `outreach@rapidtoolreview.com` |
| `B2B_SMTP_APP_PASSWORD` | 16-char app password |
| `B2B_TEST_EMAIL` | **Your** personal inbox (where test pings land) |
| `B2B_EMAIL_FROM_NAME` | `Kim` (shows as "Kim &lt;outreach@...&gt;") |
| `B2B_EMAIL_ENABLED` | `false` until ready, then `true` |

Then:

```bash
bash scripts/install.sh
python3 -m shorts_bot.b2b.outreach_cli status
```

You should see **Outreach SMTP: yes**.

### 4. Test (sends to YOUR inbox, from the outreach address)

```bash
python3 -m shorts_bot.b2b.outreach_cli test-email --to you@your-personal-email.com
```

Or set `B2B_TEST_EMAIL` once and run:

```bash
python3 -m shorts_bot.b2b.outreach_cli test-email
```

### Agent creates the outreach Gmail (browser)

```bash
python3 -m shorts_bot.b2b.gmail_setup_cli
```

Opens **Desktop** browser → fills signup → **you** enter phone code when Google asks.  
Credentials land in `data/b2b/gmail_setup_handoff.json` (local only).  
Then create an **App Password** on that new account → `B2B_SMTP_APP_PASSWORD` in Secrets.

---

## Daily workflow

Same as before — draft, tweak, confirm send:

```bash
python3 -m shorts_bot.b2b.outreach_cli save \
  --company "SomeStartup" \
  --product "SomeTool" \
  --detail "Product Hunt launch Tuesday" \
  --channel email \
  --contact "founder@startup.com"

python3 -m shorts_bot.b2b.outreach_cli send --index 0 --confirm
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Outreach inbox not configured` | Set `B2B_SMTP_USER` + `B2B_SMTP_APP_PASSWORD` (not `GMAIL_SMTP_*`) |
| Test used wrong sender | Old test hit ops Gmail — fixed; use `B2B_SMTP_*` only |
| `No test recipient` | Pass `--to your@email.com` or set `B2B_TEST_EMAIL` |
| Auth failed | App password must be for the **outreach** account, not PayPal ops |

Send log: `data/b2b/send_log.jsonl`
