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

1. Cursor → your Cloud Agent → **Secrets**  
2. Add:
   - `GOOGLE_CLIENT_ID` = (paste Client ID)  
   - `GOOGLE_CLIENT_SECRET` = (paste Client secret)  
3. On the machine that runs the bot: `bash scripts/install.sh` (Windows: use Git Bash or WSL if you have it)

**Or** on your PC only: paste into `.env` in the project folder (same two lines as `.env.example`).

---

## Part B — Sign in once (2 minutes, on your PC)

Must run where **Chrome can open** and you're logged into your **channel Google account** (`paypalacc4progress@gmail.com`).

**Windows PowerShell** (in `proof-codex-ai` folder):

```powershell
python -m shorts_bot.youtube.auth_cli
```

If `python` fails, try `py -m shorts_bot.youtube.auth_cli`.

- Browser opens → pick your channel Google account → **Allow**  
- If no browser: copy the `http://localhost:8090` link from the terminal into Chrome  

**Success:** file exists at `data/youtube_token.json`

---

## Part C — Check it worked

```powershell
python -m shorts_bot.login_status
```

You want green checkmarks on **YouTube Analytics API** and **YouTube API upload**.

---

## Shortcut — already signed in before?

If you posted from another copy of the project, copy that machine’s file:

`data/youtube_token.json` → same path in your current `proof-codex-ai` folder.

No new sign-in needed if the token is still valid.

---

## Still stuck?

| Message | Fix |
|---------|-----|
| Missing GOOGLE_CLIENT_ID | Part A not done — keys still placeholder |
| OAuth token missing | Part B — run `auth_cli` on your PC |
| Upload scope missing | Run `auth_cli` again (it asks for consent again) |
| Cloud VM can’t upload | Token must live on the machine that uploads — use home PC or copy `youtube_token.json` |
