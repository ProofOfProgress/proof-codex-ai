# Meta app + Facebook API — owner handoff

**Goal:** Let the bot post Reels to **Peripheral Horror** without you clicking Upload every time.

---

## What the agent does (automatic)

1. Creates a Meta developer app named **Peripheral Bot** (Business type)
2. Opens **Graph API Explorer** and generates a Page token
3. Saves credentials to `data/facebook_api.json` (gitignored)

---

## What you do (one time, ~2 minutes)

### If you see “Please re-enter your password” on Desktop

1. Look at the **Desktop browser** window (not this chat)
2. Type your **Facebook password**
3. Click **Submit**

The agent waits up to 10 minutes, then finishes on its own.

### After the app exists

Add these to **Cursor → Cloud Agent → Secrets**:

| Secret name | Value |
|-------------|--------|
| `FACEBOOK_PAGE_ID` | `61590716288819` |
| `META_PAGE_ACCESS_TOKEN` | starts with `EAA…` (agent saves it locally first) |

Then on the VM:

```bash
bash scripts/install.sh
python3 -m shorts_bot.integrations.api_setup_cli --status
```

---

## Test autopost (draft #5)

```bash
python3 -m shorts_bot.production.closed_loop_cli --draft-id 5 --facebook
```

---

## Commands

```bash
# Create app + token (opens Desktop browser)
python3 -m shorts_bot.integrations.meta_app_create_cli

# Token only (if app already exists)
python3 -m shorts_bot.integrations.meta_app_create_cli --token-only

# Full status matrix
python3 -m shorts_bot.integrations.api_setup_cli --status
```
