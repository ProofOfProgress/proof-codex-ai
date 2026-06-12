# Gmelius + Slack for Gmail — owner setup

**Native channel email (Option A) already works** — Gmail SMTP → `#peripheral-ops`. This doc is for **extra** integrations you asked for.

---

## Three different things (don’t mix them up)

| Thing | Where it “lives” | Shows in Slack Apps? |
|-------|------------------|----------------------|
| **Channel email** (Option A) | Slack channel Integrations | No — not an app |
| **Slack for Gmail™** | Gmail right sidebar add-on | **No** — installs in Google, not Slack |
| **Gmelius** | Chrome extension + Gmelius cloud + Slack bot | **Yes** — `@gmelius` after connect |

If Slack **Apps** doesn’t list “Gmail”, that’s normal — the official Gmail add-on never appears there.

---

## Gmelius (shared inbox ↔ Slack)

Paid with free trial. Syncs shared Gmail labels/inboxes to Slack channels; reply from Slack.

### Step 1 — Chrome extension (Gmail)

1. [Chrome Web Store — Gmelius](https://chromewebstore.google.com/detail/gmelius-for-gmail-shared/dheionainndbbpoacpnopgmnihkcmnkl) → **Add to Chrome**
2. Open Gmail as `paypalacc4progress@gmail.com` → complete Google sign-in (2FA on phone)
3. Gmelius icon should appear in Gmail **right sidebar** (expand sidebar arrow if hidden)

### Step 2 — Connect Slack (from Gmelius dashboard — required order)

Slack Marketplace **Add to Slack** often jumps to help docs until Gmelius is signed in on Gmail first. Do this order:

1. [app.gmelius.com](https://app.gmelius.com) → sign in with `paypalacc4progress@gmail.com`
2. **Integrations** → **Slack** → **Add a Workspace** → pick **peripheralorg**
3. Choose `#peripheral-ops` for notifications
4. In Slack: `/invite @gmelius` in `#peripheral-ops` (private channels need this)

Gmelius Slack sync requires a **Gmelius** paid plan (Flex/Growth/Pro on gmelius.com) — not the same as Slack Pro. Free trial available.

Help: [help.gmelius.com/slack/integration](https://help.gmelius.com/slack/integration)

### Step 3 — Verify in Slack

- **Apps** sidebar should show **Gmelius**
- `@gmelius` autocomplete works in `#peripheral-ops`

---

## Slack for Gmail™ (official Google add-on)

Forward **one email at a time** from Gmail UI to a Slack channel. Free. **Does not install as a Slack app.**

### Install (personal Gmail — no Workspace admin)

1. [Google Workspace Marketplace — Slack for Gmail](https://workspace.google.com/marketplace/app/slack_for_gmail/533288507123) → **Install**
2. Approve Google 2FA on phone if prompted
3. Gmail → open any message → **right sidebar** → click **Slack** icon  
   - If missing: expand sidebar (small arrow bottom-right of Gmail)
4. Gmail → ⚙️ **Settings** → **Add-ons** → **Manage add-ons** → confirm **Slack for Gmail** enabled
5. **Connect to Slack** → workspace **peripheralorg** → send test to `#peripheral-ops`

### “Installed but icon missing”

- Side panel closed — open it
- Hard refresh Gmail (Ctrl+Shift+R)
- Settings → Add-ons → re-enable
- Personal `@gmail.com` accounts: no admin needed; Workspace accounts may need admin to allow marketplace apps

---

## What the bot uses (automated alerts)

**Not** Gmelius or Slack for Gmail — those are for **you** in the browser.

Automated pipeline alerts use:

```bash
python3 -m shorts_bot.integrations test   # Gmail SMTP → channel email
```

Secrets: `SLACK_CHANNEL_EMAIL`, `GMAIL_SMTP_USER`, `GMAIL_SMTP_APP_PASSWORD`

---

## If Slack app install says “can’t perform this action”

- You need **workspace owner/admin** to approve marketplace apps
- **Settings & administration** → **Manage apps** → allow members to install apps
- Or owner installs Gmelius from [Slack Marketplace](https://slack.com/marketplace/AG8S1RKCK-gmelius) first

---

## Current status (agent)

| Item | Status |
|------|--------|
| Gmelius Chrome extension | Installed in Desktop Chrome |
| Gmelius Slack app | Pending — needs Gmelius account + Slack connect from dashboard |
| Slack for Gmail add-on | Pending — blocked on Google 2FA (tap Yes + code on iPhone) |
| Channel email SMTP | **Working** after address regenerate |

After 2FA on phone, say **“2FA done”** and the agent can finish Gmail add-on + Gmelius Slack connect.
