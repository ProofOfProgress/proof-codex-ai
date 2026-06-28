---
name: knowledge-gather
description: Ask the knowledge gatherer to read course files and return a plain-English briefing with sources. Use for rules, launch steps, module cheat sheets, or any question answerable from data/research/course/ and docs/.
---

# /knowledge-gather — course & strategy librarian

Background employee. Reads **knowledge files only** — no scout, no clips, no posting.

## Examples

```
/knowledge-gather
What are the Module 1 video don'ts I need before launch?

/knowledge-gather
Brief me on week 1 — $1k in 7 calendar days, midnight launch, 8-10 posts

/knowledge-gather
Module 3 product checks — what EchoTik can't do vs what I verify manually

/knowledge-gather
What's left on LAUNCH_TODO before we can post at midnight?
```

## What you get back

- Short direct answer  
- Bullet facts  
- **Source file paths**  
- Gaps if the docs don't cover it  

## CEO orchestration

The main agent can also dispatch `knowledge-gatherer` in background while you work on install or buys:

> "Gather Module 7 misinformation rules while I finish the laptop"

Watch: `python3 -m shorts_bot.agent_ops tail --mission latest`

Full roster: `/team` · `docs/FOR_OWNER_AGENT_TEAM.md`
