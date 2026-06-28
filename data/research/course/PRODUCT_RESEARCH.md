# Product research (owner override)

**Course:** `module_03_product_research_strategies.md`  
**Automation:** EchoTik scout → `data/tiktok_shop/products.json`  
**Agent:** `/product-research` subagent (`product-researcher`)

Kalodata filters **hardcore lurkers** and **100 gap** are course sauce — **not fully automated in EchoTik yet**. Use Kalodata manually for those; EchoTik runs **middle core** and **200 method** presets.

---

## EchoTik presets (automated)

| CLI preset | Course name | When to use |
|------------|-------------|-------------|
| `middle_core` | Middle core | Default — strong weekly movers |
| `two_hundred` | 200 method | Yesterday hot list, growth filter |

```bash
python3 -m shorts_bot.tiktok_shop.scout_cli status
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 10
python3 -m shorts_bot.tiktok_shop.scout_cli list
```

Saved picks: `data/tiktok_shop/products.json`

Secrets: `ECHOTIK_USERNAME` + `ECHOTIK_PASSWORD` — see `docs/FOR_OWNER_ECHOTIK_SETUP.md`

---

## Manual checks (course — agent reminds you, you verify in Kalodata)

From `kalodata_rules.PRODUCT_CHECKS` + Module 3:

- **6+ of 10** top affiliate videos show purple **ad** badge (brand spending on GMV Max)
- Creator list has **variety** — not only the brand's own shop
- **Commission $** worth posting (price × rate)
- **Brand match** — image, title, shop name align; skip rip-off / random-letter sellers
- **Revenue trend** rising — skip products trending down
- **Testing mindset** — speed + volume of tests wins (course)

EchoTik scout **scores** GMV, creators, commission, videos — it does **not** see Kalodata ad badges or trend charts. Owner spot-checks finalists in Kalodata before committing.

---

## Pipeline hook (CEO)

1. **Research** → `product-researcher` (background) saves + ranks picks  
2. Owner picks one → Module 4 image  
3. **Prompt** → `product-video-prompt-builder`  
4. Kling render → **edit** → **QC** → post  

Group calls / owner notes beat stale filters — update this file when strategy shifts.
