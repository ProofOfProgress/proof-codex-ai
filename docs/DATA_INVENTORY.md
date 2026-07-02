# Data inventory — what the agent actually has (2026-07-02)

Honest trust checklist. **Weekly Drop is reference only — not used for picks.**

## Momentum Academy (Playwright crawl)

| Area | Status | Path |
|------|--------|------|
| Dashboard, course stages | ✅ | `data/research/course/inbox/momentum-deep/` |
| Resources (FAQs, violations, software, VA, etc.) | ✅ 60 pages | same |
| Resources scroll-below-fold | ⚠️ partial | re-crawl with scroll |
| Weekly Drop | ✅ scraped | **reference only** — not scout source |
| Product Scout UI rules | ✅ | `momentum_scout_rules.yaml` |
| Furniture prompts | ✅ | `momentum-deep/060-course-g-furniture-products.md` |
| EOD | ignored per owner | — |
| Coach call 2026-06-30 | ✅ | `inbox/coach-call-2026-06-30*.md` |

## Discord (Edge + desktop helper)

| Area | Status |
|------|--------|
| Logged in (proofofprogressyt) | ✅ |
| Momentum server (white M icon) | ✅ owner on page |
| Full channel scrape | 🔄 in progress |
| Playwright Discord profile | not needed — Edge session used |

## Product research (autonomous picks)

| Backend | Status |
|---------|--------|
| **Kalodata filter URLs** | ❌ need furniture + high-ticket list URLs on hub |
| KaloPilot API | optional |
| FastMoss API | optional |
| Weekly drop → products.json | **DISABLED** — owner rule |

**Coach filters (Kalodata):** 7d rev >$10k · video source · 30%+ growth · **price >$80** · creators ≤200 · commission ≥8% · **furniture category easiest**

## Phones

| Item | Status |
|------|--------|
| phone_1 Moto G (`ZT422C55M8`) | ✅ bound via Windows ADB |

## Commission vs product price

Scout report format: **`$19.50/sale (13% of $150 product)`** — the first number is **your commission**, not the product price.

## To finish autonomous research

1. Kalodata logged in on hub Edge
2. Apply filters: **Furniture** + coach call filters + high ticket ($80+)
3. Paste filter URL → `data/tiktok_shop/kalodata_filters.json` preset `furniture_high_ticket`
4. `python3 -m shorts_bot.tiktok_shop.scout_autorun` — pulls from Kalodata, not weekly drop
