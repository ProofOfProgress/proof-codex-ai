# YouTube connection — simple checklist (no coding)

Two things must exist before the bot can upload or pull stats:

1. **Google app keys** (`GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`) — like a username/password for the *app*, not your channel  
2. **Your one-time “Allow”** — saves `data/youtube_token.json` on the machine that runs the bot  

---

## Part A — Google app keys (10 minutes, in browser)

1. Open https://console.cloud.google.com/  
2. Create or pick a project (e.g. **Shorts Bot**)  
3. **APIs & Services → Library** — enable:
   - **YouTube Data API v3**
   - **YouTube Analytics API**
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**  
   - If asked, configure **OAuth consent screen** (External, add your Gmail as test user)  
   - Application type: **Desktop app**  
   - Name: **Shorts Bot**  
5. Copy **Client ID** and **Client secret**

### Add keys to Cursor (recommended)

1. Cursor → your **Cloud Agent** → **Secrets** (not only IDE settings)  
2. Add:
   - `GOOGLE_CLIENT_ID` = (paste Client ID)  
   - `GOOGLE_CLIENT_SECRET` = (paste Client secret)  
3. On the machine that runs the bot: `bash scripts/install.sh`  
4. Check: `grep GOOGLE_CLIENT .env` must **not** say `your-client-id`

**Or** on your PC only: paste into `.env` in the project folder (same two lines as `.env.example`).

---

## Part B — Sign in once (2 minutes)

**Do not use Playwright / YouTube Studio browser for this** — Google often says “This browser or app may not be secure.” Use **API OAuth** instead.

### Option 1 — Same machine (Desktop tab or home PC)

```bash
python3 -m shorts_bot.youtube.auth_cli connect
```

- Browser opens in **real Chrome** (Cursor Desktop tab on cloud VM) → pick channel Google account → **Allow**
- If no browser: copy the `http://127.0.0.1:8090` link from the terminal into Chrome

### Option 2 — Phone or home PC (cloud VM can’t open Chrome)

On the VM:

```bash
python3 -m shorts_bot.youtube.auth_cli url
```

1. Open the printed URL on your **phone or home PC** (Safari/Chrome — not the bot browser)
2. Sign in → Allow
3. Copy the **full redirect URL** from the address bar (`http://127.0.0.1:8090/?code=...`)
4. On the VM:

```bash
python3 -m shorts_bot.youtube.auth_cli url --complete 'PASTE_FULL_URL_HERE'
```

### Option 3 — Auth at home, paste token to cloud

1. On home PC: run `auth_cli connect` → get `data/youtube_token.json`
2. Cursor → **Cloud Agent → Secrets** → add `YOUTUBE_TOKEN_JSON` = entire file contents
3. On VM: `bash scripts/install.sh`

**Success:** file exists at `data/youtube_token.json`

---

## Part C — Check it worked

```bash
python3 -m shorts_bot.login_status
```

You want green checkmarks on **YouTube Analytics API** and **YouTube API upload**.

---

## Shortcut — already signed in before?

If you posted from another copy of the project, copy that machine’s file:

`data/youtube_token.json` → same path in your current `proof-codex-ai` folder.

Or add the file contents as Cursor secret `YOUTUBE_TOKEN_JSON` and run `bash scripts/install.sh`.

No new sign-in needed if the token is still valid.

---

## Still stuck?

| Message | Fix |
|---------|-----|
| Missing GOOGLE_CLIENT_ID / still placeholder | Keys in **IDE secrets** don’t reach the cloud VM — use **Cloud Agent → Secrets**, then `bash scripts/install.sh` |
| “Browser not secure” (Google) | Stop using Playwright/Studio login — use `auth_cli connect` or `auth_cli url` (Part B) |
| OAuth token missing | Part B — run `auth_cli connect` or paste token via `YOUTUBE_TOKEN_JSON` secret |
| Upload scope missing | Run `auth_cli connect` again (consent prompt) |
| Cloud VM can’t upload | Token must be on the VM — `YOUTUBE_TOKEN_JSON` secret or complete `auth_cli url` flow |
