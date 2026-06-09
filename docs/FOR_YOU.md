# For you (no coding knowledge needed)

## Can the bot create a YouTube channel by itself?

**Almost — but Google blocks one step.**

Google requires a **phone number or security check** the first time anyone creates an account. No bot on earth can skip that legally. It's Google's rule, not ours.

### What the bot DOES do automatically

1. Opens a real browser
2. Goes to Google sign-up or YouTube
3. Creates your channel once you're logged in
4. **Saves the login** so it never asks again

### What you do ONCE (about 2–5 minutes)

When Google shows **phone verification** or **CAPTCHA**:
- Enter your phone code in the browser window
- That's it. You never paste code. You never use a terminal.

After that one time, the bot handles the rest.

## How to start channel setup

Tell the bot in chat:

> Set up my YouTube channel called "Helpful Shorts"

Or ask me (the cloud agent) to run it for you in the Desktop pane.

## You do NOT need to

- Paste any code
- Understand Python
- Click "merge" on GitHub (the agent does that)
- Install anything unless we ask for one API key later

## What we need from you eventually

| Item | Why | How hard |
|------|-----|----------|
| Phone number | Google account (one time) | 2 minutes |
| Channel name | What to call it | Tell us in plain English |
| OpenAI API key | Full chat tonight (separate from ChatGPT Pro) | **docs/CHAT_TONIGHT.md** — 2 minutes |

That's the whole list for now.

## Channel status

Your YouTube channel is **live** and logged in. You set the name yourself — the bot saved the session and won't fight you for browser control unless you ask.

**Next:** the bot drafts Short scripts → you approve → later CapCut + upload.

## Run at home (start here)

**docs/RUN_AT_HOME.md** — pull, `bash scripts/run-all.sh`, done. Only login steps need you.

## Chat tonight (before YouTube setup)

Follow **docs/CHAT_TONIGHT.md**:

1. Get API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Run `bash scripts/set-openai-key.sh` (paste key once)
3. Run `bash scripts/start.sh` → **http://localhost:8080**

Header should say **Chat: full**. Then talk normally — ask for Short ideas, drafts, niche help.

## Installed — how to use (no coding)

Someone already ran install for you. To open the bot:

1. Run: `bash scripts/install.sh` (only once; already done in cloud)
2. Start chat page: `python3 -m shorts_bot.web`
3. Open **http://localhost:8080** in your browser

### What you'll see

- **Left:** chat with the bot (type normally)
- **Right:** **Yes / No** buttons for:
  - **Self-improvements** (pros & cons listed — bot learning)
  - **Script drafts** (approve before posting)

No paste. No terminal after setup — just the web page.

## YouTube Analytics (learns on its own)

The bot uses Google's **official** YouTube Analytics API — not screen scraping.

**First time at home:** follow **docs/TOMORROW.md** (3 steps: Google keys → paste in `.env` → one browser sign-in).

**Every day after that:**

1. `bash scripts/start.sh`
2. Open **http://localhost:8080**
3. Tap **Sync YouTube Analytics**
4. Tap **Yes — do this** or **No** on each suggestion (pros & cons listed)

The bot pulls real stats, scores your Shorts, and proposes up to 3 improvements per sync so sign-off stays easy.

## Discord (talk from your phone)

Your **public key** is saved. You still need the **bot token** once — see **docs/MORNING.md**.

Then run `bash scripts/run-all.sh` and message the bot `!help`.

It can DM you a morning briefing, take Yes/No decisions, and queue dev/coding work for approval.
