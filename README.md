# Shorts Bot

Jenny Hoyos–trained strategist for a faceless, human-approved YouTube Shorts channel.

The bot uses course files 01–09 (idea, hook, retention, visuals, editing, analytics) plus verbatim transcript rules. It helps you ideate, draft scripts, and learn from analytics. **North star:** 100% AI-automated Shorts channels that make money without ongoing human ops. **Today:** strong script + learning layer; **building next:** video render, upload, daily autopilot (see [docs/PRIORITIES.md](docs/PRIORITIES.md)). **Free-first stack:** CapCut, YouTube Audio Library, Canva free, Google Drive.

**Don't code?** Read [docs/FOR_YOU.md](docs/FOR_YOU.md) — plain English on what the bot does and what you do once.

## Install

```bash
bash scripts/install.sh
```

## Quick start — web chat (recommended)

```bash
python3 -m shorts_bot.web
```

Open **http://localhost:8080** — chat on the left, **Yes/No** approvals on the right.

## CLI chat

```bash
cp .env.example .env   # add keys as needed (see docs/)
bash scripts/run-all.sh   # web + Discord
docs/RUN_AT_HOME.md    # complete home guide
docs/QUICKSTART.md     # one-page start
docs/MORNING.md        # wake-up checklist
make test              # run tests
python3 -m shorts_bot
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

## Course knowledge base

```
course/
  files/01-09_*.md     # Structured retrieval (ChatGPT-organized)
  verbatim/            # Word-for-word transcript rules
  router_prompt.md     # Jenny strategist instructions
  free_services.md     # Free / free-tier tool stack
```

## Priorities (top 4 only)

See **[docs/PRIORITIES.md](docs/PRIORITIES.md)** — ranked for money + full automation.

| # | Building now | Status |
|---|--------------|--------|
| 1 | Video factory (script → voice → visuals → `.mp4`) | Not started |
| 2 | YouTube upload API (no Studio clicks) | Not started |
| 3 | Daily autopilot runner | Not started |
| 4 | Remove human Yes/No gates (auto QC + publish) | Not started |

## What works today

| Step | Status |
|------|--------|
| Ideas + script drafts | Yes |
| Quality checks + course routing | Yes |
| Human approve / reject drafts | Yes (to be automated in #4) |
| Analytics sync + reward learning | Yes |
| Video render + upload + daily post | **No** |

## Roadmap

- [x] Talk to a bot
- [x] Jenny Hoyos course integrated (files 01–09)
- [x] Draft Short scripts with quality checks
- [x] Approve / reject + feedback memory
- [x] YouTube analytics sync + reward loop
- [x] Free services reference (CapCut, YouTube Audio Library, etc.)
- [ ] Video factory (TTS + visuals + render)
- [ ] YouTube upload API + auto-publish
- [ ] Daily autopilot (unattended loop)
- [ ] Fully automated QC (no human gates)
