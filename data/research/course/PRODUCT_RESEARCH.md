# Product research (owner override)

**Course:** `module_03_product_research_strategies.md`  
**Automation:** EchoTik scout → `data/tiktok_shop/products.json`  
**Agent:** `/product-research` subagent (`product-researcher`)

**Owner / course creator (2026-06-28):** **FastMoss is as good as Kalodata** for research. Use **FastMoss** for manual finalist checks (not Kalodata). FastMoss has an API ([developer.fastmoss.com](https://developer.fastmoss.com/)) — scout v2 may integrate later.

Kalodata filter names (**hardcore lurkers**, **100 gap**) still appear in Module 3 video — replicate logic in FastMoss filters or EchoTik presets over time; **not fully automated yet**.

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

## Manual checks (course — verify in FastMoss)

Module 3 checks the EchoTik scout **cannot** see — owner (or future FastMoss API) on **finalists only**:

| Check | Plain English |
|-------|----------------|
| **Ad spend** | Top affiliate videos — brand running **paid ads** (FastMoss “ads” / GMV Max signals; course: purple Ad on many top 10) |
| **Trend** | Sales chart **going up**, not falling |
| **Brand match** | Image, title, shop name align — skip rip-off sellers |
| **Commission $** | Price × rate worth your time |
| **Creator mix** | Not only the brand’s own shop promoting |
| **Volume** | Test many products fast — course mindset |

EchoTik narrows the list; **FastMoss confirms** the picks EchoTik can’t fully validate.

---

## Pipeline hook (CEO)

1. **Research** → `product-researcher` (background) saves + ranks picks  
2. Owner approves in **FastMoss** (8–10 for launch)  
3. **Prompt** → `product-video-prompt-builder`  
4. Kling render → **edit** → **QC** → post  

Group calls / owner notes beat stale filters — update this file when strategy shifts.
