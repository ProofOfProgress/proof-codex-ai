# Recraft setup — for the owner (plain English)

Your **$100 annual Basic** plan is for the Recraft **website** (daily credits). The bot uses the **API** — separate **API units** (~$1 per 1,000 units, ~40 units per still on V3).

---

## Step 1 — Browser (agent opens this for you)

```bash
python3 -m shorts_bot.production.recraft_setup_cli --open-browser
```

In Cursor, click the **Desktop** tab. You should see three tabs:

| Tab | What to do |
|-----|------------|
| **Profile** | Sign in → buy **API units** if balance is 0 → click **Generate** → copy API key |
| **Studio** | Open your funny-character **custom style** → ⋯ menu → **Copy style ID** |
| **Pricing** | Reference only (~40 units per image) |

---

## Step 2 — Cursor Secrets

Open **Cursor → your Cloud Agent → Secrets** and add:

| Secret name | Set to |
|-------------|--------|
| `RECRAFT_API_KEY` | Paste the key from Profile → Generate |
| `RECRAFT_STYLE_ID` | Paste the UUID from your custom style |
| `IMAGE_PROVIDER` | `recraft` |
| `CAPTION_MODE` | `off` |
| `BURN_IN_SUBTITLES` | `false` |
| `VISUAL_STYLE` | `ai` (stills lane — not Blender/Kling) |

Optional (defaults are fine):

| Secret name | Default |
|-------------|---------|
| `RECRAFT_MODEL` | `recraftv3` (required for custom style) |
| `RECRAFT_IMAGE_SIZE` | `1024x1820` (9:16 Shorts) |

---

## Step 3 — Sync and verify

```bash
bash scripts/install.sh
python3 -m shorts_bot.production.recraft_setup_cli
```

All rows should be **OK** in green.

---

## Step 4 — Test one frame (no full Short yet)

```bash
python3 -m shorts_bot.production.image_cli --prompt "funny crayon horror character alone in apartment at 3am, vertical, no text"
```

Open `data/production/test_ai_frame.png` — should match your Recraft style.

---

## Important: web plan vs API

| | Website (your $100/year) | API (bot automation) |
|--|--------------------------|----------------------|
| Credits | Daily web credits | Prepaid **API units** |
| Billing | Annual Basic | ~$1 per 1,000 units in Profile |
| Custom style | Yes in Studio | Same style via `RECRAFT_STYLE_ID` |

You need **both**: web plan for making styles in Studio, API units for the bot to generate frames.

---

## If something fails

| Error | Fix |
|-------|-----|
| No **Generate** button on Profile | Buy API units first (balance must be > 0) |
| Style looks wrong in bot | Confirm `RECRAFT_MODEL=recraftv3` (V4 does not use custom style_id yet) |
| 401 invalid key | Re-copy key; run `bash scripts/install.sh` |
| 0 API units | Buy more in Profile (~$5 = ~5,000 units ≈ 125 stills on V3) |
