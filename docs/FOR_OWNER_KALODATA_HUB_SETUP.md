# Kalodata hub UI scout

**Agent applies filters on the hub** with **verify-before-submit gates** — you do not paste URLs unless the agent aborts.

---

## Misclick protection (system fix 2026-07)

Blind coordinate clicking opened **product detail** tabs and set wrong filters (Last 30 Days, growth >0%). Fixed:

| Gate | What it does |
|------|----------------|
| **List page only** | Must be `kalodata.com/product` — never `/product/detail` |
| **Sidebar clicks only** | Refuses clicks with x > 380 (left filter panel) |
| **Gemini verify** | Reads screenshot JSON — **aborts if vision fails** (no blind clicks) |
| **Pre-submit verify** | Dates, growth %, commission %, price, creators must match course method |
| **No Submit** until verify passes | Won't click Submit on bad state |
| **Tab cleanup** | `--cleanup-tabs` closes duplicate Ovios/couch tabs |

```bash
# From cloud agent (drives your HP via desktop helper):
python3 scripts/hub_kalodata_apply_method.py --method middle_core --category Furniture --cleanup-tabs
python3 scripts/hub_kalodata_apply_method.py --method hundred_gap --category Furniture --cleanup-tabs
```

Methods: `hardcore`, `lurkers`, `hundred_gap`, `middle_core`, `two_hundred` — swap `--category` only.

**Deprecated:** `cloud_kalodata_grind.py` (blind clicks).

---

## Owner checklist (minimal)

| # | You do | Time |
|---|--------|------|
| **1** | Kalodata **paid** account logged in on hub Edge | once |
| **2** | Leave **one** tab on product list — or let agent `--cleanup-tabs` | — |
| **3** | Agent runs `hub_kalodata_apply_method.py` per method × category | automatic |

Optional fallback: paste filter URL manually → `python3 scripts/kalodata_set_filter_url.py middle_core 'URL'`

---

## Why this is the best path

| You do once | Agent does every scout |
|-------------|------------------------|
| Log into Kalodata on hub | Open your saved filter URL |
| Apply filters in UI, copy URL | Capture product list (API + table) |
| Paste URL into one JSON file | Score + save `products.json` |

KaloPilot AI is optional fallback. **Saved URLs beat AI** for filter accuracy.

---

## One-time setup (~10 minutes)

### Step 1 — Log in on the hub

On the HP (WSL terminal):

```bash
cd ~/proof-codex-ai
python3 -m shorts_bot.browser.cli open kalodata --minutes 10
```

Log into Kalodata in the browser window. Close when done — session saves to `data/browser_profile/kalodata/`.

### Step 2 — Copy filter URLs (one per preset)

For each preset you use:

1. Open [kalodata.com/product](https://www.kalodata.com/product)
2. Apply the course filters (see below)
3. Click **Apply / Submit**
4. Copy the **full browser address bar URL**
5. Paste into `data/tiktok_shop/kalodata_filters.json` under that preset's `"filter_url"`

**Start with these two:**

| Preset | Course filters (Module 3) |
|--------|---------------------------|
| `middle_core` | Last 7 days · revenue growth ≥50% · creators ≤200 · commission ≥20% |
| `two_hundred` | **Yesterday** · revenue growth ≥100% · creators ≤200 |

**Sauce presets** (when ready):

| Preset | Notes |
|--------|--------|
| `hardcore_lurkers` | Copy from course / Miro saved filter |
| `hundred_gap` | Yesterday-based — may be empty some days |

### Step 3 — Test on hub

```bash
python3 -m shorts_bot.tiktok_shop.scout_cli status
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 10
```

From cloud agent:

```bash
bash scripts/scout_on_hub.sh run --preset middle_core --limit 10
```

---

## Optional: force backend

| Secret / env | Effect |
|--------------|--------|
| `SCOUT_PROVIDER=auto` | Hub URL first, then KaloPilot, then FastMoss |
| `SCOUT_PROVIDER=hub_ui` | Kalodata saved URLs only |
| `SCOUT_PROVIDER=kalodata` | KaloPilot token only |

---

## If session expires

Re-run Step 1 (open kalodata, log in). Filter URLs stay the same — no need to re-copy.

---

## File to edit

`data/tiktok_shop/kalodata_filters.json` — only field the agent needs is `"filter_url"` per preset.

See also: `docs/FOR_OWNER_KALODATA_OR_FASTMOSS.md`
