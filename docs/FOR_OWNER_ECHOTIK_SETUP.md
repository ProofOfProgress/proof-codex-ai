# EchoTik — TikTok Shop product scout API

Sign up: https://echotik.live → **API Platform** → create API key.

EchoTik uses **HTTP Basic auth** (username + password from the dashboard).

---

## Cursor Secrets

| Secret | What to put |
|--------|-------------|
| `ECHOTIK_USERNAME` | API username |
| `ECHOTIK_PASSWORD` | API password |
| `ECHOTIK_REGION` | `US` (optional) |

```bash
bash scripts/install.sh
python3 -m shorts_bot.tiktok_shop.scout_cli status
```

Docs: https://opendocs.echotik.live/en

---

## Scout (technical — no strategy)

```bash
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 10
python3 -m shorts_bot.tiktok_shop.scout_cli list
```

Results: `data/tiktok_shop/products.json`

**Which products to pick** = your **paid course**, not this repo.

Basics: `docs/FOR_OWNER_BASICS.md`
