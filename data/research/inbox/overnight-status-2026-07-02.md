# Overnight status — 2026-07-02 (agent while owner sleeps)

## Product research

### Working
- **Quality gate** — every product checked: price ≥$80, commission ≥8%, creators ≤200, GMV ≥$10k, blocks weekly-drop junk
- **`scout_cli validate`** — audit any list
- **Live Edge scrape path** — desktop screenshot → Gemini table parse → quality gate (tested on hub)
- **Playwright DOM apply** — filter specs + verify (when session not Cloudflare-blocked)
- **Hub Gemini synced** from cloud via `scripts/sync_hub_agent_secrets.py`

### Blocked (one owner action)
- **`KALODATA_PILOT_TOKEN` not on hub or cloud** — best hands-off path. Add from kalodata.com/pilot → Cursor secrets → new agent run.
- **Edge CDP** — port 9222 not reachable from WSL yet (needs Edge started with `--remote-debugging-address=0.0.0.0` on Windows)
- **Live scrape** — reads screen when Kalodata list visible; Gemini parse needs **filters applied** on screen (middle core / Furniture). Last run: products seen but none passed GMV/commission gate.

### Cleared
- `products.json` emptied — old weekly-drop picks were all rejected (GMV $24–$473, not $10k+)

### Commands (hub)
```bash
python3 scripts/hub_live_scout_run.py      # Kalodata visible in Edge
python3 scripts/hub_kalodata_e2e.py        # CDP + Playwright apply
python3 -m shorts_bot.tiktok_shop.scout_cli validate
```

## Discord
- **210 Momentum server screenshots** captured → `data/desktop_hub/discord_momentum/`
- Gemini summarize → `data/research/course/inbox/discord-momentum-scrape-YYYY-MM-DD.md` (running)
- Playwright web crawl blocked on hub (async loop) — desktop scrape path used instead

## Did NOT do (cannot without owner)
- Create new Kalodata/KaloPilot accounts with random email — needs owner's paid account token
- Log into owner's Kalodata in Playwright without token or CDP

## Wake-up checklist for owner
1. Add `KALODATA_PILOT_TOKEN` to Cursor secrets (2 min) OR leave Kalodata filtered list full-screen in Edge
2. New agent run → I run `scout_autorun` + validate
3. Confirm first product row shows real revenue ($10k+) before we Kling
