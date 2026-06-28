---
name: affiliate-ceo
description: Start orchestrated affiliate pipeline work — CEO delegates to specialists in parallel and logs everything to the mission feed.
---

# /affiliate-ceo

Invoke the **Affiliate CEO** orchestrator.

The CEO will:

1. Create a **mission log** (so you can watch progress)
2. Delegate to specialist employees (`product-video-prompt-builder`, `module1-qc-runner`, `video-caption-writer`)
3. Keep working while **background** employees run (QC, long tasks)
4. Tell you how to watch the mission feed

## Examples

```
/affiliate-ceo
Coordinate Module 5 video prompt + caption for this product image

/affiliate-ceo
Run QC in background on outputs/clip.mp4 while you prep the post caption

/affiliate-ceo
Full pipeline for "Wireless car charger" — product image attached
```

## Watch the workflow

```bash
python3 -m shorts_bot.agent_ops tail --mission latest
```

Or open http://127.0.0.1:8080/agent-ops after `python3 -m shorts_bot.web`

See also: `/team` for the full roster.
