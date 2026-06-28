# EchoTik — TikTok Shop product scout API

Sign up: https://echotik.live → **API Platform** → create API key.

EchoTik uses **HTTP Basic auth** (username + password from the dashboard).

---

## Cursor Secrets (recommended)

Add these in **Cursor → Cloud Agent → Secrets** (exact names), then **start a new agent run**:

| Secret | What to put |
|--------|-------------|
| `ECHOTIK_USERNAME` | API username |
| `ECHOTIK_PASSWORD` | API password |
| `ECHOTIK_REGION` | `US` (optional) |

The VM syncs them into `.env` via `bash scripts/install.sh`. **Do not paste keys in chat** — rotate if exposed.

---

## Verify

```bash
bash scripts/install.sh
python3 -m shorts_bot.tiktok_shop.scout_cli status
python3 -m shorts_bot.tiktok_shop.scout_cli ping      # 1 API call — quota + latest data
python3 -m shorts_bot.tiktok_shop status              # factory dashboard row
```

**Quota:** Free/trial plans have limited calls. If you see `Usage Limit Exceeded`, upgrade at echotik.live or wait for reset. Scout uses several calls per run (ranklist + product detail batches).

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
