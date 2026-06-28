# Agent team — CEO + employees

Plain-English guide for running parallel specialist agents and watching what they do.

---

## Who is the CEO?

**The main agent in every chat is the CEO** — that's who you talk to when you open a new Cursor chat. There is **no** `/affiliate-ceo` subagent.

The CEO delegates to **employees** (subagents). Employees do one job each. You can also talk to any employee directly with `/their-name`.

---

## Important: employees don't remember other chats

Subagents **cannot access previous chats** or earlier messages in your session. Each time the CEO sends work to an employee, the CEO must paste in:

- File paths, product name, caption text
- Mission id (if logging)
- Exactly what to do and what to return

The **mission log** (`data/agent_ops/missions/`) is how you watch work across steps — not employee memory.

---

## What you have

| Role | Who | How to talk |
|------|-----|-------------|
| **CEO** | Main agent (every chat) | Just chat normally — "make a clip for this product" |
| **Employee** | Product Video Prompt Builder | `/product-video-prompt-builder` + product image |
| **Employee** | Video Caption Writer | `/video-caption-writer` |
| **Employee** | Video Editor | `/video-editor` — loop + caption burn |
| **Employee** | Module 1 QC Runner | `/module1-qc-runner` (runs in background) |
| **Roster + status** | — | `/team` |

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

Just tell the main agent:

```
Make a clip for this product — video prompt, caption, edit, and QC
```

The CEO creates a **mission**, delegates to employees (with full context in each dispatch), and keeps working while background jobs run.

---

## Watch the workflow (CEO ↔ employees)

Every orchestrated run writes events to a **mission log**.

### Terminal

```bash
python3 -m shorts_bot.agent_ops missions
python3 -m shorts_bot.agent_ops tail --mission latest
python3 -m shorts_bot.agent_ops status --mission latest
```

### Web dashboard

```bash
python3 -m shorts_bot.web
```

Open: **http://127.0.0.1:8080/agent-ops**

---

## What each log event means

| Event | Who | Meaning |
|-------|-----|---------|
| `mission_created` | CEO | New pipeline run started |
| `dispatch_background` | CEO | Sent work to employee — CEO keeps going |
| `dispatch_foreground` | CEO | Sent work to employee — waits for result |
| `completed` / `failed` | Employee | Step result |

---

## Typical affiliate clip flow

1. **You** ask the CEO to make a clip
2. **CEO** creates mission → **prompt builder** (video prompt)
3. Render in Higgsfield/Kling
4. **CEO** → **video editor** (background) + **caption writer** (foreground)
5. **CEO** → **QC runner** (background)
6. CEO summarizes — upload only if QC passed

---

## Troubleshooting

**CEO doesn't delegate**

- Use Agent mode (not Ask mode)
- Ask explicitly: "Delegate the video prompt to product-video-prompt-builder"

**Employee seems confused**

- They didn't get enough context — CEO must paste paths, product name, and mission id in every dispatch

**No mission log**

- CEO must run `python3 -m shorts_bot.agent_ops mission new ...`
