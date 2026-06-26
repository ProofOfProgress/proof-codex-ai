# TikTok login — posting API

> **Recommended:** Use **Zernio** instead — `docs/FOR_OWNER_ZERNIO_SETUP.md`  
> Direct TikTok API below is **hard mode** (developer app, OAuth, tokens per account).

Connect TikTok so the bot can upload clips.

**Time:** ~15 minutes first time.

---

## Step 1 — TikTok developer app

1. Open https://developers.tiktok.com/ and log in  
2. **Manage apps** → **Create app**  
3. Add product: **Content Posting API** → enable **Direct Post**  
4. **Redirect URI** (exact):
   ```
   http://127.0.0.1:8091/
   ```
5. Copy **Client key** and **Client secret**

---

## Step 2 — Secrets

Cursor → Cloud Agent → **Secrets**:

| Secret | Value |
|--------|--------|
| `TIKTOK_CLIENT_KEY` | Client key |
| `TIKTOK_CLIENT_SECRET` | Client secret |

Then on the VM:

```bash
bash scripts/install.sh
```

---

## Step 3 — OAuth (one time)

```bash
python3 -m shorts_bot.tiktok.auth_cli url
```

1. Open the printed URL  
2. Log in → **Allow**  
3. Copy the full redirect URL from the address bar (`http://127.0.0.1:8091/?code=...`)  
4. Run:

```bash
python3 -m shorts_bot.tiktok.auth_cli url --complete 'PASTE_FULL_URL_HERE'
python3 -m shorts_bot.tiktok.auth_cli status
```

---

## Step 4 — Test upload

```bash
python3 -m shorts_bot.tiktok.upload_cli path/to/clip.mp4 --title "Test clip"
```

---

## Notes

- Unaudited apps may post **private only** until TikTok approves the app.  
- Redirect URI must match the portal exactly (`8091`).  
- Scopes default: `user.info.basic,video.publish` — see `.env` `TIKTOK_OAUTH_SCOPES` if you need draft inbox mode.

Secrets list: `docs/CURSOR_SECRETS.md`
