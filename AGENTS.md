# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

**Shorts Bot** — Jenny Hoyos strategist CLI for faceless Shorts. Course KB in `course/files/` (01–09) + `course/verbatim/`. Free-first stack: CapCut, YouTube Audio Library, Canva free. API LLMs + future Playwright for CapCut.

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

### Course

Jenny Hoyos course is in `course/`. Router picks files 01–09 per user message. Offline: `course <question>` and `free tools` commands.

### Next phases

YouTube analytics reward loop, CapCut Playwright operator — not implemented yet.
