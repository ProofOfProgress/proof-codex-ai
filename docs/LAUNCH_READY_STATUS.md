# Launch ready status — agent grind session 2026-07-02

Plain-English snapshot for owner when you get back.

## Product research — **works autonomously today**

```bash
python3 -m shorts_bot.tiktok_shop.scout_autorun
```

- Picks from **Momentum weekly drop** + course filter rules (creators ≤200, commission, price)
- Writes `data/tiktok_shop/products.json` + `data/tiktok_shop/scout_report.txt`
- **Kalodata** kicks in when real filter URLs are pasted (not product detail links)
- Top picks last run: NOBULL shoes, Momcozy washer, ice maker, Wahl trimmer, Mermaid brush

## Momentum Academy — **scraped**

- 60 pages in `data/research/course/inbox/momentum-deep/`
- Weekly drop JSON: `data/tiktok_shop/momentum_weekly_drop.json` (23 products)
- Scout rules: `data/tiktok_shop/momentum_scout_rules.yaml`

## Discord — **scraped via Edge + desktop helper**

- No Playwright needed — uses your logged-in Edge session
- Intel in `data/research/course/inbox/discord-desktop-crawl-*.md` and `discord-full-crawl-*.md`
- DMs captured (Moe: Kalodata API ~$500/mo, automation 10/day, prompt builder refs)

## Phones

- ADB path: `~/android-sdk/platform-tools/adb` (already installed on hub)
- Plug phone → unlock → tap **Allow USB debugging** → `bash scripts/hub_adb_windows.sh`
- If empty: Admin PowerShell `scripts/hub_usbipd_attach.ps1`

## Bubble accounts

- **2 at launch** (not 4) — see `.cursor/rules/bubble-two-accounts.mdc`

## Still needs one-time owner (not blocking affiliate clips)

| Item | Action |
|------|--------|
| Kalodata filter URLs | Log in on hub Edge → apply filters → paste list URLs in `kalodata_filters.json` |
| Phone USB | Allow debugging prompt when plugged in |
| Affiliate TikTok account | Purchased account + Zernio when ready to post |

## Commands (agent or you)

```bash
# Product picks
python3 -m shorts_bot.tiktok_shop.scout_autorun

# Discord hard scrape (hub, Edge logged in)
bash scripts/hub_discord_full_scrape.py   # on hub
python3 scripts/process_discord_full.py   # on cloud

# Hub intel pull
bash scripts/hub_pull_intel.sh
```
