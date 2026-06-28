---
name: team
description: Show the agent team roster, how to talk to each employee, and latest mission status. Use when the owner wants to see who's available, watch CEO activity, or check parallel work.
---

# /team — your agent employees

## CEO = main agent (not a subagent)

You talk to the **CEO in every normal chat** — there is no `/affiliate-ceo` employee. The CEO delegates to the specialists below.

**Subagents cannot see prior chats.** The CEO must paste full context (paths, product name, mission id) every time it dispatches work.

## Roster (employees only)

| Employee | Slash | Job | Background? |
|----------|-------|-----|-------------|
| **Product Video Prompt Builder** | `/product-video-prompt-builder` | Module 5 Kling/Higgsfield **video prompts** | No |
| **Product Researcher** | `/product-research` | Module 3 EchoTik scout (background) | **Yes** |
| **Video Caption Writer** | `/video-caption-writer` | Module 6 on-screen caption copy | No |
| **Video Editor** | `/video-editor` | Pan loop + caption burn (~10s finish) | **Yes** |
| **Module 1 QC Runner** | `/module1-qc-runner` | Pre-upload violation check | **Yes** |

## Talk to CEO or any employee

**CEO (orchestrate):** just chat — e.g. "Make a clip for this product — prompt, edit, QC"

**Direct to employee:**

```
/product-research
Run middle core scout — top picks for this week

/product-video-prompt-builder
(video prompt — attach product image)

/video-caption-writer
Pain-point caption for a car phone mount

/video-editor
Loop and burn caption: input raw.mp4 → output final.mp4 — caption: "Your hook"

/module1-qc-runner
QC: path/to/final.mp4 product "Car mount"
```

## Watch CEO ↔ employee workflow

```bash
python3 -m shorts_bot.agent_ops tail --mission latest
python3 -m shorts_bot.web   # → http://127.0.0.1:8080/agent-ops
```

Full guide: `docs/FOR_OWNER_AGENT_TEAM.md`
