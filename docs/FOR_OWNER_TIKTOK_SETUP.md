# TikTok setup — plain English

Connect TikTok so the bot can upload your finished Shorts (same MP4 as YouTube).

**Time:** ~15 minutes first time.  
**Cost:** TikTok developer account is free. Posting uses your normal TikTok account.

---

## What you need first

1. A **TikTok account** (use the one you want for AI product reviews)
2. TikTok app switched to **Business/Creator** if TikTok asks (personal accounts may be limited for API — use Creator account)

---

## Step 1 — Create TikTok developer app

1. Open **https://developers.tiktok.com/** and log in
2. **Manage apps** → **Create app**
3. Name it something like `AI Product Reviews Bot`
4. Add product: **Content Posting API**
5. Enable **Direct Post**
6. **Redirect URI** — add exactly:
   ```
   http://127.0.0.1:8091/
   ```
7. Copy **Client key** and **Client secret**

---

## Step 2 — Add keys to Cursor Secrets

In Cursor → Cloud Agent → **Secrets**, add:

| Secret name | Value |
|-------------|--------|
| `TIKTOK_CLIENT_KEY` | Client key from portal |
| `TIKTOK_CLIENT_SECRET` | Client secret from portal |

On the VM run:

```bash
bash scripts/install.sh
```

---

## Step 3 — Connect your TikTok account (one time)

On your **home PC** or phone browser:

```bash
python3 -m shorts_bot.tiktok.auth_cli url
```

1. Open the URL it prints  
2. Log into TikTok → **Allow** posting  
3. Browser may show “can't connect” — that's OK  
4. Copy the **full address bar URL** (starts with `http://127.0.0.1:8091/?code=`)  
5. Run:

```bash
python3 -m shorts_bot.tiktok.auth_cli url --complete 'PASTE_FULL_URL_HERE'
```

Check:

```bash
python3 -m shorts_bot.tiktok.auth_cli status
python3 -m shorts_bot.login_status
```

---

## Step 4 — Upload a test video

After InVideo gives you an MP4:

```bash
python3 -m shorts_bot.tiktok.upload_cli data/production/draft_1/final_short.mp4 \
  --title "ChatGPT Plus — Pay or Skip? #aitools #techreview"
```

---

## Important: unaudited apps = private posts first

Until TikTok **audits** your app, uploads may be **private only**. That's normal.

To go public later: TikTok developer portal → submit app for **Content Posting API audit** (can take 1–4 weeks). Keep posting private while learning — hooks and scripts still matter.

---

## Scopes

Default: `user.info.basic` + `video.publish` (direct post).

If TikTok rejects `video.publish` in sandbox, temporarily set in `.env`:

```
TIKTOK_OAUTH_SCOPES=user.info.basic,video.upload
```

That sends videos to **drafts inbox** instead of auto-post — you tap Post in TikTok app.

---

## If stuck

Run status and send the output to the agent:

```bash
python3 -m shorts_bot.tiktok.auth_cli status
```

Common fixes:
- Redirect URI mismatch → must match portal **exactly** (`8091` not `8090`)
- Missing `video.publish` → re-connect after enabling Direct Post in portal
- `unaudited_client` → post as private until audit passes
