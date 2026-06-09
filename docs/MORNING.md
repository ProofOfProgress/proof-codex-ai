# Good morning — what's ready

## Start everything

```bash
bash scripts/install.sh          # if first time on this machine
bash scripts/doctor.sh           # shows what's missing
bash scripts/run-all.sh          # web + Discord together
```

- **Web:** http://localhost:8080
- **Discord:** message the bot `!help` (after bot token is set)

---

## Your Discord public key

Already saved in `.env` as `DISCORD_PUBLIC_KEY`.

You still need **`DISCORD_BOT_TOKEN`** (secret) from Discord Developer Portal:

1. [discord.com/developers/applications](https://discord.com/developers/applications)
2. Your app → **Bot** → **Reset Token** → copy
3. Paste in `.env` as `DISCORD_BOT_TOKEN=...`
4. Enable **Message Content Intent** under Bot settings
5. **OAuth2 → URL Generator** → scopes: `bot`, `applications.commands` → invite bot to your server
6. Set `DISCORD_OWNER_ID` to your **numeric** user ID (see below)

Then: `python3 -m shorts_bot.discord_bot`

### Username ≠ user ID

`isaac_proofofprogress_50448` is your **username** — the bot cannot use that for DMs.

Your user ID is a long **number only**, like `123456789012345678`.

**How to copy it (30 seconds):**

1. Discord app → **User Settings** (gear) → **Advanced**
2. Turn on **Developer Mode**
3. Close settings. **Right-click your avatar/name** (top-left or in a server member list)
4. Click **Copy User ID**
5. Paste into `.env`:

```
DISCORD_OWNER_ID=123456789012345678
```

(No quotes. Numbers only.)

On connect, the bot DMs you a **morning briefing** (and anyone in `DISCORD_NOTIFY_IDS`).

---

## Only needs you (login)

| Item | Command / doc |
|------|----------------|
| Google YouTube Analytics | `docs/TOMORROW.md` |
| OpenAI full chat (optional) | `docs/CHAT_TONIGHT.md` |
| Discord bot token | above |

Everything else works without those.

---

## Discord commands

```
!help !status !chat <msg> !draft <topic> !pending
!yes <id> !no <id>     — improvements
!draftyes <id>         — approve draft
!sync                  — YouTube Analytics
!dev <title> | <desc>  — queue coding work
!devyes <id> !devno <id>
!briefing              — morning checklist again
```

---

## Web UI panels

- **Chat** — strategist (full with OpenAI key, offline without)
- **Rewards** — YouTube sync + score history
- **Learning** — `data/LEARNED.md` + journal
- **Dev queue** — approve coding tasks before they run
- **Right sidebar** — Yes/No improvements & drafts

---

## What's built for the long-term goal

- Reward engine with score **breakdown**
- Approved rules feed into **draft generation**
- **Dev queue** with Yes/No (path to self-coding without babysitting)
- **Discord** as remote control
- **Local hosting** — all data in `data/`, secrets in `.env`

Self-coding on autopilot comes later; the approval rails are in place now.
