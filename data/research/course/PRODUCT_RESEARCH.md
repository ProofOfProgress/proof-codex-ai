# Product research (owner override)

**Course:** `module_03_product_research_strategies.md`  
**Research tool:** **Kalodata or FastMoss** (owner choice — see `docs/FOR_OWNER_KALODATA_OR_FASTMOSS.md`).  
**Agent:** `/product-research` subagent (`product-researcher`)

---

## Stack (2026-07 owner)

| Tool | Role |
|------|------|
| **Kalodata KaloPilot** | Automated scout via `KALODATA_PILOT_TOKEN` — no Enterprise API |
| **FastMoss** | UI ~$59/mo and/or free OpenAPI trial at developers.fastmoss.com |
| ~~EchoTik~~ | **Retired** |

**Automation status:**

| Mode | When |
|------|------|
| **Kalodata KaloPilot scout** | `KALODATA_PILOT_TOKEN` + Kalodata subscription |
| **FastMoss OpenAPI scout** | Free trial keys + rank endpoints (in progress) |
| **FastMoss / Kalodata UI on hub** | Logged-in browser on HP while API blocked |

Setup: `docs/FOR_OWNER_KALODATA_OR_FASTMOSS.md`

---

## Pre-breakout lens *(owner intel — account seller, 2026-06-29)*

**North star for picks:** find products **before** they break out — not only what’s already #1.

| Signal | Why |
|--------|-----|
| **Sales/GMV accelerating** | Product is heating up, not peaked |
| **Creator count rising fast** | Others starting to pile in — still early window |
| **Ad spend appearing** | Brand investing before mass saturation |
| **New release / not yet saturated** | Room for a video to catch the wave |
| **Already top** | OK for steady posts — **future top** = highest upside (20M-view path) |

**Already-top vs future-top:**

- **Top today** = safer, more competition, smaller view ceiling per clip.
- **Future top** = literal gold — post **before** the breakout so your video rides the wave.

When owner or FastMoss UI picks 8–10 for launch, **bias toward rising / early** products that pass Module 3 checks (ads, brand match, commission $), not only established chart leaders.

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

1. **Research** → CEO delegates **`product-researcher`** (background) — pre-breakout lens, FastMoss scout when wired  
2. Agent locks **8–10** in `products.json` — no owner pick step  
3. **Prompt** → `product-video-prompt-builder`  
4. Kling → edit → QC → post (local queue until Zernio hookup)  

Group calls / owner notes beat stale filters — see `GROUP_CALLS.md`.
