# Good morning — what's ready

## Start everything

```bash
bash scripts/install.sh          # if first time on this machine
bash scripts/doctor.sh           # shows what's missing
bash scripts/start.sh            # web UI
```

- **Web:** http://localhost:8080 (chat + Yes/No approvals)
- **Briefing:** http://localhost:8080/api/briefing
- **Remote:** Slack `@cursor` — see `docs/SLACK_CURSOR_SETUP.md`

---

## Only needs you

| When | What |
|------|------|
| First time | Google API keys + `python3 -m shorts_bot.youtube.auth_cli` |
| Optional | `GEMINI_API_KEY` for full chat (free tier) |
| Money / 2FA | Browser login when agent opens Desktop tab |

---

## Automated (no tap)

- Analytics sync on a timer
- Safe improvements auto-Yes
- Daily Short when `AUTO_DAILY_ENABLED=true` in `.env`
- Comment triage (light auto-reply)

---

## Quick commands (web chat)

| Type | Does |
|------|------|
| `daily` | Full autopilot Short |
| `sync` | YouTube analytics |
| `pending` | What needs Yes/No |
| `research <topic>` | Deep research |
| `help` | Full list |
