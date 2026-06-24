# Printify API — hook the bot to your POD store

**Yes, Printify has an API.** Docs: https://developers.printify.com/

The bot can list **your** products and pull **mockup photos** for Kling clips — no manual image hunt.

---

## What you do (one time, ~5 min)

### 1. Create Printify account
- https://printify.com (Premium when ready — not required for API token)

### 2. Generate API token
1. Log in to Printify  
2. Open **My Profile → Connections** (or go to https://printify.com/app/account/api)  
3. Click **Generate** personal access token  
4. Copy the token (shown once)

### 3. Add to Cursor Secrets

| Secret | Value |
|--------|--------|
| `PRINTIFY_API_TOKEN` | Your token |

Optional (if you have multiple shops):

| Secret | Value |
|--------|--------|
| `PRINTIFY_SHOP_ID` | Shop ID number from `printify_cli shops` |

### 4. Sync on the VM

```bash
bash scripts/install.sh
python3 -m shorts_bot.tiktok_shop.printify_cli status
```

You want **green** “Printify: configured”.

---

## What the bot can do with the API

| Feature | Status |
|---------|--------|
| List shops | ✅ |
| List **your** products | ✅ |
| Pull hero mockup image | ✅ → Kling clip |
| Create products / upload designs | 🔜 later |
| Orders / webhooks | 🔜 later |

**TikTok Shop connection** (Seller Center ↔ Printify) is still done in Printify’s dashboard — the API doesn’t replace that link. Connect those **after** Seller signup tomorrow.

---

## Daily commands

```bash
# Check connection
python3 -m shorts_bot.tiktok_shop.printify_cli status

# List shops (find shop id)
python3 -m shorts_bot.tiktok_shop.printify_cli shops

# Save your products locally
python3 -m shorts_bot.tiktok_shop.printify_cli sync

# List cached products
python3 -m shorts_bot.tiktok_shop.printify_cli products

# Clip YOUR product (after first listing exists)
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --printify-title "Your shirt name"
```

---

## Flow (seller)

1. Design in Canva → publish product in **Printify**  
2. `printify_cli sync`  
3. `factory_cli make-clip --printify-title "..."`  
4. Post on your shop TikTok with product tag  

EchoTik = research what sells. **Printify API = your actual listings.**

---

## If status fails

| Error | Fix |
|-------|-----|
| not configured | Add `PRINTIFY_API_TOKEN` to Secrets, run `install.sh` |
| no shops | Create Printify account; connect TikTok store later |
| product not found | Run `printify_cli sync` after publishing listing |
