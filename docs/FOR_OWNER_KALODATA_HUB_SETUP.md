# Kalodata hub UI scout — minimal owner setup

**Goal:** You paste filter URLs **once**. The agent loads them on your hub PC — **no filter clicking**, highest quality (exact course presets).

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
