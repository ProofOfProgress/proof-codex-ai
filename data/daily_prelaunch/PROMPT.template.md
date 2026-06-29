# Daily pre-launch CEO mission — paste into Cursor Cloud Agent (or auto-typed by desktop helper).

Mission: **{mission_name}** · `{mission_id}` · **{date}** ({timezone})

---

Run today's **affiliate video prep** during warmup. **Do not post to Zernio** on `affiliate_main` until owner says launch is close.

## Hard rules

- **Agent owns product research** — owner does not pick products or paste names
- **Zero strikes** — Module 1 + TOS QC before any clip is marked ready; regen until pass
- **No Zernio** on purchased affiliate account yet
- **Never freestyle Module 5 prompts** — use `product-video-prompt-builder`
- Log mission: `python3 -m shorts_bot.agent_ops mission new` + every dispatch

## Today's plan

Read: `data/daily_prelaunch/today_plan.json`

- **Clips target:** {clips_target}
- **Products scheduled:** {product_list}

## Execute (in order)

1. **Confirm plan** — read `today_plan.json`; if scout failed, run FastMoss scout / product-researcher and refresh plan
2. **Per product** (CEO orchestrates subagents):
   - Module 4 sample → `product-video-prompt-builder` → Kling render → `video-editor` (pan loop + caption) → `module1-qc-runner`
3. **Queue locally** — QC-passed MP4s only; no upload
4. **Report** — plain English: how many clips ready, any blocked, what's next

## Watch mission

```bash
python3 -m shorts_bot.agent_ops tail --mission {mission_id}
```

Start now.
