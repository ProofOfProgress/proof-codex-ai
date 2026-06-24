# EchoTik — TikTok Shop product research API

Sign up: https://echotik.live → **API Platform** → create API key.

EchoTik uses **HTTP Basic auth** (username + password from the API dashboard — not a single Bearer token).

---

## Cursor Secrets

| Secret | What to put |
|--------|-------------|
| `ECHOTIK_USERNAME` | API username from EchoTik dashboard |
| `ECHOTIK_PASSWORD` | API password from EchoTik dashboard |
| `ECHOTIK_REGION` | `US` (optional — default US) |

Then:

```bash
bash scripts/install.sh
python3 -m shorts_bot.tiktok_shop.scout_cli status
```

**Free trial:** 100 API calls — enough to test product scout.

Docs: https://opendocs.echotik.live/en

---

## Scout products (replaces Kalodata until Charm call)

**Middle core** (7-day style — commission + creator cap):

```bash
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 10
```

**200 method** (yesterday hot movers):

```bash
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset two_hundred --limit 10
```

Results save to `data/tiktok_shop/products.json`.

---

## Daily habit

1. `scout_cli run` each morning  
2. Pick top 3–5 products  
3. Kling 5s clip → `factory_cli loop-clip` → `enqueue` → `post-batch`

Full factory doc: `docs/FOR_OWNER_TIKTOK_SHOP_FACTORY.md`

---

## vs Charm.io (your call in 2 days)

| | **EchoTik (now)** | **Charm.io (call)** |
|---|-------------------|---------------------|
| **API** | Public, self-serve | Enterprise / demo sales |
| **Cost** | ~$10–20/mo + API credits | Usually higher — brand/retail tier |
| **Best for** | Bot pulls products daily | Deep SKU + brand intelligence |
| **Use** | **Now** until Charm proves worth it | Compare on call — ask for API + pricing |

Don't buy Charm on the call unless they show **Shop product data you can't get from EchoTik** for your price.
