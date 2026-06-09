# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

**Shorts Bot** — conversational CLI for a faceless, human-approved YouTube Shorts channel. No local video generation. API LLMs + future Playwright operators for CapCut / video sites.

### Services

No long-running server. Run the bot interactively:

```bash
pip install -r requirements.txt
python -m shorts_bot
```

Set `OPENAI_API_KEY` in `.env` for full conversational mode. Without it, offline command mode still works (`help`, `draft`, `pending`, etc.).

### Lint / test

No linter configured. Smoke checks:

```bash
pip install -r requirements.txt
python -m compileall -q shorts_bot
python -m pytest tests/ -q
```

### Data

SQLite at `data/shorts_bot.db` (gitignored). Stores drafts, approvals, rejections, chat history.

### Next phases

Course ingest, YouTube analytics, Playwright site operators — not implemented yet.
