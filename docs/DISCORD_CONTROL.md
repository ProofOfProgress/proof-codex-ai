# Control Soft Continuity from Discord

## Start the bot

```bash
python3 -m shorts_bot.discord_bot
# or
bash scripts/run-all.sh   # web + Discord
```

**Developer Portal checklist:**
1. **Message Content Intent** — ON (required)
2. Invite URL scopes: `bot` + `applications.commands`
3. `.env`: `DISCORD_BOT_TOKEN`, `DISCORD_OWNER_ID` (your numeric user ID from `!myid`)

## How to talk to the bot

| Where | How |
|-------|-----|
| **DM** | Type normally — no `!` prefix |
| **Server** | `!command` or `@SoftContinuity your message` |
| **Owner in server** | Plain text works (set `DISCORD_OWNER_ID`) |
| **Slash** | `/daily` `/status` `/draft` `/pending` `/briefing` |

## Pipeline commands (API-first — minimal browser)

| Command | What it does |
|---------|----------------|
| `daily` | Full autopilot Short |
| `daily <topic>` | Same with topic |
| `research <topic>` | Deep research (web + vidIQ + competitors) |
| `deep research <topic>` / `!deepresearch` | Force refresh — re-browse web |
| `finish video <id>` | Paid finish pipeline |
| `apply brand` | Name + description + banner via **YouTube API** |
| `generate assets` | Build profile.png + banner.png locally |
| `login status` | Service health |
| `!live` | Same as login status |

## Agent memory (persistent rules)

The bot remembers operating rules across sessions (like ChatGPT memory).

| Command | What it does |
|---------|----------------|
| `remember <text>` / `!remember <text>` | Save a rule or fact |
| `operating rule: <text>` | Save as pinned operating rule |
| `memory` / `!memory` / `rules` | List saved memories |
| `forget <id>` / `!forget <id>` | Delete a memory |

Exported to `data/MEMORY.md`. See `docs/AGENT_MEMORY.md`.

## Channel branding

See `docs/CHANNEL_BRANDING.md`. Profile picture is still a **one-time manual** upload in Studio (API limitation).
