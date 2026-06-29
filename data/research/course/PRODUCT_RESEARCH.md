# Product research (owner override)

**Course:** `module_03_product_research_strategies.md`  
**Research tool:** **FastMoss only** — replaces EchoTik and Kalodata (course creator: as good as Kalodata).  
**Agent:** `/product-research` subagent (`product-researcher`)

---

## Stack (2026-06-28 owner)

| Tool | Role |
|------|------|
| **FastMoss** | **Only** product research — rankings, trends, ad signals, Module 3 checks |
| ~~EchoTik~~ | **Retired** — do not pay or configure for new work |
| ~~Kalodata~~ | **Retired** — use FastMoss instead |

**Automation status:**

| Mode | When |
|------|------|
| **FastMoss API scout** | When `FASTMOSS_CLIENT_ID` + secret configured + scout migration shipped |
| **FastMoss UI → owner picks** | **Launch fallback** — you pick 8–10 in FastMoss app; tell agent product names |

Saved picks: `data/tiktok_shop/products.json`

Setup: `docs/FOR_OWNER_FASTMOSS_SETUP.md` · Engineering: `docs/FASTMOSS_SCOUT_PLAN.md`

---

## Module 3 checks (FastMoss)

What “high quality” means — FastMoss can show most of this (UI today; API when wired):

| Check | Plain English |
|-------|----------------|
| **Ad spend** | Top videos — brand running paid ads (course: many purple Ad badges on top 10) |
| **Trend** | Sales **going up**, not falling |
| **Brand match** | Image, title, shop name align |
| **Commission $** | Price × rate worth posting |
| **Creator mix** | Variety — not only brand self-promo |
| **Filters** | middle core, 200 method, hardcore lurkers, 100 gap — use FastMoss filters equivalent to course |

---

## EchoTik presets (legacy — do not use)

Old bot presets `middle_core` / `two_hundred` mapped to EchoTik. **FastMoss scout will use course-equivalent filters** when API integration lands. Until then: pick in FastMoss UI.

---

## Pipeline hook (CEO)

1. **Research** → owner in **FastMoss** (or future `product-researcher` + FastMoss API)  
2. Owner approves **8–10** for launch  
3. **Prompt** → `product-video-prompt-builder`  
4. Kling → edit → QC → post  

Group calls / owner notes beat stale filters — see `GROUP_CALLS.md`.
