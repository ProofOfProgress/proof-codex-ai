# Slack autonomy bus — agent talks to itself

**Goal:** AlphaBeta001 posts `[autonomy] <command>` in `#peripheral-ops`, a Socket Mode listener reads it (including the bot’s own messages), runs the same router as web chat (`BotOperations.chat`), and replies in the thread. No IDE required for status checks, research bursts, or pipeline steering.

This is separate from **@cursor** (Cursor’s app for starting Cloud Agents).

---

## How it works

```
Automation / API / bot itself
        │
        ▼
  post [autonomy] status
        │
        ▼
  #peripheral-ops (Slack)
        │
        ▼
  Socket Mode listener (web UI background)
        │
        ▼
  BotOperations.chat("status")
        │
        ▼
  Thread reply with result
```

**Self-talk:** Messages from the bot user that start with `[autonomy]` are executed. The bot is literally talking to itself through Slack as a durable command bus.

**Owner override (optional):** Set `SLACK_AUTONOMY_OWNER_COMMANDS=true` to also run plain human messages in the ops channel (no prefix). Default is prefix-only for safety.

---

## One-time Slack app setup

You already need `SLACK_BOT_TOKEN` + `SLACK_CHANNEL_ID` (see `docs/FOR_OWNER_SLACK_BOT.md`). Add Socket Mode:

### 1. Enable Socket Mode

1. [api.slack.com/apps](https://api.slack.com/apps) → your **AlphaBeta001** app
2. **Socket Mode** → toggle **On**
3. **Basic Information** → **App-Level Tokens** → **Generate Token**
   - Scope: `connections:write`
   - Copy token (`xapp-...`) → Cursor Secret **`SLACK_APP_TOKEN`**

### 2. Event subscriptions

1. **Event Subscriptions** → **Enable Events** → **On**
2. Subscribe to bot events:
   - `message.channels` (public channel messages)
   - `app_mention` (optional — `@AlphaBeta001 status`)
3. Save changes

### 3. Bot scopes (add if missing)

Under **OAuth & Permissions** → Bot Token Scopes:

- `chat:write` (already)
- `channels:history` — read channel messages for Socket Mode

Re-install app to workspace if scopes changed.

### 4. Cursor Secrets

| Secret | Purpose |
|--------|---------|
| `SLACK_BOT_TOKEN` | `xoxb-...` post + auth |
| `SLACK_CHANNEL_ID` | `C...` ops channel |
| `SLACK_APP_TOKEN` | `xapp-...` Socket Mode |
| `SLACK_AUTONOMY_ENABLED` | `true` (default) |
| `SLACK_AUTONOMY_OWNER_COMMANDS` | `false` (default) — set `true` to run your plain messages |

```bash
bash scripts/install.sh
python3 -m shorts_bot.web   # listener starts with background automation
```

---

## Usage

### From Slack (manual test)

Post in `#peripheral-ops`:

```
[autonomy] status
```

AlphaBeta001 should reply in-thread with pipeline status.

### From CLI / API

```bash
python3 -m shorts_bot.integrations autonomy status
python3 -m shorts_bot.integrations autonomy "take 5m research horror hooks" --note "nightly burst"
```

```bash
curl -X POST http://127.0.0.1:8080/api/slack/autonomy \
  -H "Content-Type: application/json" \
  -d '{"command":"status"}'
```

### From code / automations

```python
from shorts_bot.integrations.slack_autonomy import post_autonomy_command

post_autonomy_command("status", note="hourly heartbeat")
```

---

## Status

```bash
curl -s http://127.0.0.1:8080/api/slack/status | jq .autonomy
```

- `socket_ready` — all three tokens/channel configured
- `active` — listener can execute commands
- `prefix` — always `[autonomy]`

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Command posts but never executes | Web UI must be running (`python3 -m shorts_bot.web`). Socket Mode runs in background thread. |
| `socket_ready: false` | Add `SLACK_APP_TOKEN` (`xapp-`) and correct `SLACK_CHANNEL_ID`. |
| Bot posts but ignores own messages | Ensure message starts with `[autonomy]` (case-insensitive). |
| Wrong channel | `SLACK_CHANNEL_ID` must match `#peripheral-ops` ID exactly. |
| Duplicate replies | Rare race on restart; dedupe uses message `ts`. |

---

## Security

- Default: only `[autonomy]` prefixed messages run — including from the bot itself.
- Owner plain-text commands are **off** unless you opt in.
- Keep `#peripheral-ops` private to trusted workspace members.
- `@cursor` remains separate; do not confuse GitHub Copilot replies with this bot.
