# Agent team — CEO + employees

Plain-English guide for running parallel specialist agents and watching what they do.

---

## What you have

| Role | Name | How to talk to them |
|------|------|---------------------|
| **CEO** | Affiliate CEO | `/affiliate-ceo` — coordinates everyone |
| **Employee** | Product Video Prompt Builder | `/product-video-prompt-builder` + product image |
| **Employee** | Video Caption Writer | `/video-caption-writer` |
| **Employee** | Video Editor | `/video-editor` — loop + caption burn |
| **Employee** | Module 1 QC Runner | `/module1-qc-runner` (runs in background) |
| **Roster + status** | — | `/team` |

You can talk to **any employee directly**, or ask the **CEO** to coordinate several at once.

---

## Two ways to work

### 1. Direct (you → one employee)

Best when you know exactly what you need.

```
/product-video-prompt-builder
```

Attach the Module 4 product image. You get one paragraph — paste into Higgsfield → Video → Kling 2.6.

### 2. Orchestrated (you → CEO → employees in parallel)

Best for full clip prep or when QC should run while other work continues.

```
/affiliate-ceo
Make a clip for this product — video prompt, caption, and QC
```

The CEO creates a **mission**, delegates to employees, and keeps working while background jobs (like QC) run.

---

## Watch the workflow (CEO ↔ employees)

Every orchestrated run writes events to a **mission log**.

### Terminal

```bash
# List recent missions
python3 -m shorts_bot.agent_ops missions

# Watch live feed (replace MISSION_ID or use latest)
python3 -m shorts_bot.agent_ops tail --mission latest

# Short summary
python3 -m shorts_bot.agent_ops status --mission latest
```

### Web dashboard

```bash
python3 -m shorts_bot.web
```

Open in browser: **http://127.0.0.1:8080/agent-ops**

The page auto-refreshes every few seconds. Click a mission to see the full timeline:

- CEO dispatches (`dispatch_background`, `dispatch_foreground`)
- Employee starts / completes / fails
- What each step said

---

## What each log event means

| Event | Who | Meaning |
|-------|-----|---------|
| `mission_created` | CEO | New pipeline run started |
| `started` | CEO or employee | Step began |
| `dispatch_background` | CEO | Sent work to employee — CEO keeps going |
| `dispatch_foreground` | CEO | Sent work to employee — waits for result |
| `completed` | Employee | Step finished OK |
| `failed` | Employee | Blocked or error |
| `owner_message` | You | Direct message logged for traceability |

---

## Typical affiliate clip flow (CEO mode)

1. **CEO** creates mission
2. **Prompt builder** (foreground) → Kling video prompt from product image
3. You or CEO render in Higgsfield/Kling
4. **Video editor** (background) loops clip + burns caption while **caption writer** refines hook text if needed
5. **QC runner** (background) checks finished MP4
6. CEO summarizes — upload only if QC passed

---

## Files (for reference)

| What | Where |
|------|-------|
| Employee definitions | `.cursor/agents/*.md` |
| Slash shortcuts | `.cursor/commands/` |
| Mission logs | `data/agent_ops/missions/*.jsonl` |
| Video prompt rules | `data/research/course/PROMPT_BUILDER.md` |

Mission logs stay on your machine — not committed to git.

---

## Troubleshooting

**CEO doesn't delegate to employees**

- Use Agent mode (not Ask mode)
- Pick a model that supports subagent Task delegation
- Say explicitly: "Use the affiliate-ceo subagent" or `/affiliate-ceo`

**No mission log appearing**

- CEO must run `python3 -m shorts_bot.agent_ops mission new ...`
- Check `data/agent_ops/missions/` exists after first run

**Want to resume a background employee**

- Cursor returns an agent ID when background work starts
- Say: "Resume agent ABC123 and summarize QC results"
