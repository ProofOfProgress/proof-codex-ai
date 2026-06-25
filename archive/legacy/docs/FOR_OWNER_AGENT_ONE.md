# InVideo Agent One — plain English

**Agent One** is InVideo's chat filmmaker inside **ai.invideo.io** — you talk back and forth; it writes the script and builds the video.

This is **different** from our old MCP hook (which only starts a project URL).

---

## What the bot can do now

| Layer | What it is |
|-------|------------|
| **Agent One chat** | Full conversation — best for Shorts with your twin |
| **MCP (backup)** | One-shot project URL — limited, no chat |

Command:

```bash
python3 -m shorts_bot.invideo.agent_one_cli --open-browser "30s ChatGPT Plus review, Pay Skip Wait, 9:16, my AI twin"
```

Or test login:

```bash
python3 -m shorts_bot.invideo.agent_one_cli --test
```

---

## You must stay logged in

Agent One uses **your browser session** (same as when you signed in).

If session expires → run:

```bash
python3 -m shorts_bot.invideo.handoff_cli
```

---

## Typical flow

1. Agent sends prompt to **Agent One** (Desktop browser opens)
2. Pick **New project** if InVideo asks
3. Agent One replies with plan / script — you read it in chat
4. You click **Generate** when happy (uses credits)
5. Export MP4 → tell agent **upload draft N**

---

## Agent mode vs Autopilot

- **Agent One (Agent mode)** — director chair, scene by scene ← **we use this**
- **Autopilot** — one-click full video, less control

Toggle is at the top of ai.invideo.io after login.

---

## Limits (honest)

- No public REST API for Agent One chat yet — browser bridge only
- Backend is `pro-copilot-v45.invideo.io` (WebSocket) — needs your login
- Official MCP only exposes `generate-video-from-script` (beta, 1 tool)

When InVideo ships more MCP tools, we plug them in automatically.
