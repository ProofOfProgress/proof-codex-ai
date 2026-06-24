# Priorities — North Star (re-assessed 2026-06-24)

**North star:** Make money from **100% AI-automated TikTok Shop** — seller model, faceless product clips, scout → render → post → learn.

**Rule:** Only the **top 4** below.

---

## Honest status (2026-06-24)

| Area | Status |
|------|--------|
| EchoTik product scout | **Live** — credentials + `scout_cli run/list` |
| Kling render pipeline | **Built** — `factory_cli render/make-clip`; **blocked on Kling credits** |
| Seller path playbook | **Ingested** — guru transcript + operating rules in agent memory |
| Zernio autopost | **Waiting** — need `accounts.json` + owner Seller signup |
| YouTube / RTR / InVideo | **Parked** — not current focus |

---

## Top 4 — work these only

| # | Priority | Done when |
|---|----------|-----------|
| **1** | **TikTok Seller signup + Printify** — owner opens Seller Center, links TikTok + Printify | Shop bag on profile; can tag products in drafts |
| **2** | **Clip factory end-to-end** — scout → Kling 5s → loop → queue → post (1 account first) | One product clip rendered and posted without manual ffmpeg |
| **3** | **Kling credits + daily scout loop** — `prep-images` + `make-clip` on autopilot schedule | 3–5 clips/day queued for seller TikTok |
| **4** | **Affiliate recruitment playbook** — 30% collab messages + GMV Max test budget doc | First 5 affiliate creators contacted on a winning SKU |

---

## Bot commands (owner)

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli status
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 10
python3 -m shorts_bot.tiktok_shop.factory_cli prep-images --force
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "Product name"
```

Owner checklist: `data/tiktok_shop/OWNER_NEXT_STEPS.md`

---

## Stop doing

- Ms. Byte / character Shorts (authenticity gap)
- New Replicate I2V unless owner asks (`AI_VIDEO_GENERATION_ENABLED=false`)
- 3× affiliate account model without follower growth or bought accounts
- YouTube RTR daily loop until Shop path is earning
