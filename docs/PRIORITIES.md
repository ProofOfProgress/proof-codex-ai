# Priorities — North Star (committed 2026-06-24)

**North star:** Make money from **100% AI-automated TikTok Shop seller** — Printify POD, faceless 1080p clips, scout → render → post → learn.

**Owner commitment:** TikTok Shop only. Clipping, YouTube RTR, Ms. Byte, and horror Shorts are **parked**.

**Rule:** Only the **top 4** below. Canonical list also in `data/PRIORITIES.md`.

---

## Honest status (2026-06-24)

| Area | Status |
|------|--------|
| EchoTik product scout | **Live** |
| Kling 1080p render + loop | **Live** — first clip (`speak_love_loop.mp4`) queued |
| Seller + Printify | **Waiting** — TikTok Shop signup (owner blocked until unlock) |
| Zernio autopost | **Waiting** — `accounts.json` after seller TikTok linked |
| First **own** POD product | **Not started** — next after seller signup |

---

## Top 4 — work these only

| # | Priority | Done when |
|---|----------|-----------|
| **1** | **TikTok Seller signup + Printify** | Shop bag on profile; can tag products |
| **2** | **First own product clip posted** | Your Canva design → Printify → bot clip → you post |
| **3** | **Daily factory loop** | 3–5 clips/day on your listings without manual editing |
| **4** | **Affiliates + GMV Max on winners** | 5 creators contacted; small ad test on a seller SKU |

---

## Bot commands

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli status
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 10
python3 -m shorts_bot.tiktok_shop.factory_cli prep-images --force
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "Your product name"
```

---

## Stop doing

- Clipping platforms (pay-per-view celebrity clips)
- Ms. Byte / character Shorts
- YouTube RTR / InVideo daily loop
- Pure affiliate model without 5K followers or seller account
- New Replicate I2V unless owner asks
