# Chat tonight (2 minutes)

ChatGPT Pro and the **OpenAI API** are separate. The bot needs an API key for natural conversation.

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
