# Tomorrow at home — 3 steps (no coding)

Everything is already installed in the repo. When you get home, do this once:

## Step 1 — Get Google API keys (about 10 minutes)

YouTube Analytics uses Google's **official** API (not a hack).

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (any name, e.g. "Shorts Bot")
3. **APIs & Services → Library** → enable:
   - **YouTube Analytics API**
   - **YouTube Data API v3**
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**
   - Application type: **Desktop app**
   - Name: Shorts Bot
5. Copy the **Client ID** and **Client secret**

## Step 2 — Paste keys into `.env`

Open the project folder. Edit `.env` (create from `.env.example` if needed):

```
GOOGLE_CLIENT_ID=paste-your-client-id-here
GOOGLE_CLIENT_SECRET=paste-your-client-secret-here
```

Optional (smarter chat):

```
OPENAI_API_KEY=your-openai-key
```

## Step 3 — Run the bot

In a terminal, from the project folder:

```bash
bash scripts/install.sh    # first time only
bash scripts/doctor.sh     # checks everything is OK
python3 -m shorts_bot.youtube.auth_cli   # once — browser opens, sign in with your channel Google account
bash scripts/start.sh      # opens web UI
```

Open **http://localhost:8080** in your browser.

---

## Daily use (after setup)

1. `bash scripts/start.sh`
2. Open **http://localhost:8080**
3. Tap **Sync YouTube Analytics** (pulls real stats)
4. Read each suggestion — **Pros** and **Cons** are listed
5. Tap **Yes — do this** or **No** (one tap, no typing)

That's it. The bot learns from what you approve.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Add Google API keys" | Complete Step 1–2 |
| "Run auth_cli" | Run `python3 -m shorts_bot.youtube.auth_cli` once |
| Browser won't open | Copy the URL from the terminal into Chrome |
| "No video data yet" | Upload at least one Short, wait a few hours, sync again |
| Chat feels dumb | Add `OPENAI_API_KEY` to `.env` (optional) |

Run `bash scripts/doctor.sh` anytime — it tells you what's missing.

---

## What the bot does on its own

- Pulls **official** YouTube Analytics (views, likes, comments, retention)
- Scores each video vs Jenny course benchmarks
- Proposes **up to 3 improvements** per sync (easy sign-off)
- Remembers what you approved for future drafts

You never paste code. You only tap Yes or No.
