# Chat tonight (2 minutes)

## Free option: Gemini (recommended)

1. Open [aistudio.google.com/apikey](https://aistudio.google.com/apikey) (same Google account as YouTube is fine)
2. Create an API key
3. Add to Cursor secrets as **`GEMINI_API_KEY`** or paste into `.env`:

```
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.0-flash
```

4. Restart the bot — header shows **Chat full (Gemini)**

Gemini free tier is enough for drafting scripts and strategist chat. The bot prefers Gemini over OpenAI when both are set.

---

## OpenAI (optional, paid)

ChatGPT Pro and the **OpenAI API** are separate. The bot needs an API key for natural conversation.

## I have ChatGPT Pro — why can't we use that?

**Short answer:** Pro is for *you* chatting in the ChatGPT app. The Shorts Bot is a *program* on your computer that must call OpenAI in the background — that only works through the **API**, which Pro does not include.

| | ChatGPT Pro | OpenAI API |
|---|-------------|------------|
| What it is | Subscription to chatgpt.com / the app | Developer access for apps and scripts |
| Who uses it | You, in a browser | Our bot, automatically |
| Works with Shorts Bot? | No (no official hook-in) | Yes |
| Billing | Monthly Pro fee | Pay per use (often pennies per chat with our small model) |

**What you can do with Pro today:** brainstorm in the ChatGPT app, then paste ideas into the bot — or use **offline mode** (`draft <topic>`, `course <question>`) without any API key.

**What the API unlocks:** natural back-and-forth in **http://localhost:8080**, auto-drafting scripts, and smarter improvement suggestions — all without you copying between apps.

There is no official way to "log the bot into" your Pro account. Screen-scraping ChatGPT would be fragile and is not something we build.

## Easiest way (Cursor / cloud)

1. In Cursor, add a secret named **`OPENAI_API_KEY`**
2. Paste your key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys) (starts with `sk-`)
3. Tell the agent to restart the bot, or run:

```bash
bash scripts/install.sh   # syncs the secret into .env
bash scripts/start.sh
```

4. Open **http://localhost:8080** — header should say **Chat: full**

## At home (no Cursor)

```bash
bash scripts/set-openai-key.sh
```

Paste your key when prompted. Then:

```bash
bash scripts/start.sh
```

## How to know it worked

- Web header shows **Chat: full** (not "offline")
- `bash scripts/doctor.sh` shows `OPENAI_API_KEY set`
- Bot answers in full sentences and can draft Shorts for you

## Cost note

API usage is pay-as-you-go (usually a few cents per chat). You control spending in your OpenAI account billing settings.
