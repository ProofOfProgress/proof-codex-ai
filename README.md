# Shorts Bot

Conversational operator for a faceless, human-approved YouTube Shorts channel.

The bot helps you ideate, draft scripts, and approve or reject content before anything gets posted. It learns from your feedback over time. Video production (CapCut, AI video sites, YouTube upload) comes in later phases.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env   # add your OpenAI API key
python -m shorts_bot
```

## Modes

| Mode | Requirement | What you get |
|------|-------------|--------------|
| **Full** | `OPENAI_API_KEY` in `.env` | Natural conversation + tool use |
| **Offline** | No API key | Basic commands: `draft`, `pending`, `approve`, `reject`, `stats` |

ChatGPT Pro is separate from the API. For automation and the conversational bot, use an [OpenAI API key](https://platform.openai.com/api-keys).

## Example conversation (full mode)

```
you> I want ideas for Shorts that help students focus
bot> Here are three angles...

you> Draft one about the 2-minute reset trick
bot> Created draft #1 — waiting for your approval.

you> Show pending
you> Reject 1 — too generic, give a specific example
bot> Got it. I'll avoid that pattern next time.
```

## Offline commands

```
help
draft <topic>
pending
show <id>
approve <id> [note]
reject <id> <reason>
stats
feedback
```

## Project layout

```
shorts_bot/
  bot/          # CLI + conversational agent
  drafts/       # Script generation + anti-slop checks
  approval/     # Human approval queue
  memory/       # SQLite store for drafts and feedback
data/           # Local database (gitignored)
```

## Roadmap

- [x] Talk to a bot
- [x] Draft Short scripts with quality checks
- [x] Approve / reject before posting
- [x] Learn from feedback memory
- [ ] Ingest course material
- [ ] YouTube analytics reward loop
- [ ] CapCut + video site operators (Playwright)
- [ ] Upload pipeline
