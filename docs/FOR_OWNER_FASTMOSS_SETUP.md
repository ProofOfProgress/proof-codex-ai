# FastMoss — product research (replaces EchoTik)

**FastMoss replaces EchoTik entirely** for this project (owner 2026-06-28). One research tool — not two.

Course creator: **FastMoss is as good as Kalodata** for TikTok Shop research.

---

## What you need

| Item | Where |
|------|--------|
| **FastMoss account** | [fastmoss.com](https://www.fastmoss.com/) — 7-day trial available |
| **Plan** | **Basic ~$59/mo** enough to start (verify current pricing on site) |
| **API (for bot scout)** | [developers.fastmoss.com](https://developers.fastmoss.com/) — `client_id` + `client_secret` + free trial quota |

You do **not** need EchoTik or Kalodata subscriptions.

---

## Launch path A — FastMoss app only *(until API scout ships)*

1. Subscribe to FastMoss  
2. Use course filters in the UI (middle core / 200 method / lurkers / 100 gap equivalents)  
3. Pick **8–10 products** that pass Module 3 checks (ads, trend up, brand match)  
4. Tell the agent the product names → we clip and post  

No EchoTik. No bot scout required for day one if you pick in FastMoss yourself.

---

## Launch path B — FastMoss API in the bot *(target)*

When API credentials are in Cursor Secrets:

| Secret | Value |
|--------|--------|
| `FASTMOSS_CLIENT_ID` | From developers.fastmoss.com profile |
| `FASTMOSS_CLIENT_SECRET` | Created in developer console |

Optional:

| Secret | Default |
|--------|---------|
| `FASTMOSS_API_BASE` | `https://openapi.fastmoss.com` |

Then:

```bash
bash scripts/install.sh
python3 -m shorts_bot.tiktok_shop.scout_cli status
python3 -m shorts_bot.tiktok_shop.scout_cli ping
```

**Status today:** client stub exists; **full scout migration in progress** — see `docs/FASTMOSS_SCOUT_PLAN.md`.

---

## Auth (API)

FastMoss OpenAPI flow:

1. Register → get `client_id`  
2. Create `client_secret` in console  
3. Exchange for `access_token`  
4. Call product / video / trend endpoints with token  

Docs: [FastMoss/openapi on GitHub](https://github.com/FastMoss/openapi)

---

## Budget vs old plan

| Old | New |
|-----|-----|
| EchoTik ~$125/mo | **FastMoss ~$59–139/mo** (UI tier — check site) |
| Kalodata (course login / paid) | **Included in FastMoss** |

Updates launch runway — see `docs/LAUNCH_BUDGET.md`.

---

## Legacy

EchoTik setup (do not use): `docs/FOR_OWNER_ECHOTIK_SETUP.md`
