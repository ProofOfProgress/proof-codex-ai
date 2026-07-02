# Kalodata OR FastMoss — product research setup

**Owner choice (2026-07):** Use **Kalodata** or **FastMoss** — not EchoTik. You do **not** need the $500/mo Enterprise API on either platform.

---

## Pick one

| Tool | Best for | Monthly cost | Bot automation |
|------|----------|--------------|----------------|
| **Kalodata** | Course-familiar UI + **KaloPilot AI API** | Starter ~$59–79/mo | ✅ **Works today** with pilot token |
| **FastMoss** | Course creator default | Basic ~$59/mo | ⏳ Free API **trial** + UI; rank API wiring next |

Set `SCOUT_PROVIDER=kalodata` or `fastmoss` in secrets. Default `auto` picks Kalodata if token is set, else FastMoss keys.

---

## Option A — Kalodata hub UI *(best quality — paste filter URLs once)*

**Recommended.** You apply course filters in Kalodata UI once, copy the URL, agent loads it on the hub — no clicking, no Enterprise API.

Setup: **`docs/FOR_OWNER_KALODATA_HUB_SETUP.md`**

```bash
bash scripts/scout_on_hub.sh run --preset middle_core --limit 10
```

---

## Option B — Kalodata KaloPilot *(AI fallback)*

Kalodata’s **Enterprise REST API** is still sales-only. But **KaloPilot** exposes the same data through a credit-based agent API — no Enterprise contract.

### 1. Subscribe to Kalodata

- [kalodata.com](https://www.kalodata.com/) — 7-day free trial
- **Starter** (~$59/mo annual) is enough to start

### 2. Get your pilot token

1. Log in at [kalodata.com/pilot](https://kalodata.com/pilot)
2. Bottom-left: **Connect OpenClaw** (skill install tutorial)
3. Copy **Current Account Token** (long hex string)

### 3. Add Cursor secret → new agent run

| Secret | Value |
|--------|--------|
| `KALODATA_PILOT_TOKEN` | Token from step 2 |
| `SCOUT_PROVIDER` | `kalodata` (optional — `auto` works) |

Optional:

| Secret | Default |
|--------|---------|
| `KALODATA_REGION` | `US` |

### 4. Test

```bash
python3 -m shorts_bot.tiktok_shop.scout_cli status
python3 -m shorts_bot.tiktok_shop.scout_cli ping
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 10
```

**Usage:** Each scout run consumes KaloPilot **credits** (roughly ~10 per query). Top up in Kalodata if you hit “insufficient credits.”

---

## Option B — FastMoss

### UI only (~$59/mo)

1. Subscribe at [fastmoss.com](https://www.fastmoss.com/)
2. Use filters in the app (coach-call rules in `GROUP_CALLS.md` 2026-06-30)
3. Agent can research via **hub browser** while logged in on HP (no API)

### Free API trial (no Enterprise $500)

Official OpenAPI is separate from the paid Enterprise bundle:

1. Register at [developers.fastmoss.com](https://developers.fastmoss.com/)
2. Create `client_secret` in profile
3. Apply **free trial quota**: [developers.fastmoss.com/free-trial.html](https://developers.fastmoss.com/free-trial.html)
4. Add secrets:

| Secret | Value |
|--------|--------|
| `FASTMOSS_CLIENT_ID` | From developer profile |
| `FASTMOSS_CLIENT_SECRET` | From developer console |
| `SCOUT_PROVIDER` | `fastmoss` |

```bash
python3 -m shorts_bot.tiktok_shop.scout_cli ping   # tests token exchange
```

Product **rank** endpoints are still being wired in the bot (`docs/FASTMOSS_SCOUT_PLAN.md`). Until then, use Kalodata pilot or FastMoss UI on hub.

---

## Coach filters (both tools)

From head coach call 2026-06-30 — scout applies these automatically:

- 7-day revenue > $10k · video source · 30%+ growth
- Avg price > $80 · creators ≤ 200 · commission ≥ 8%
- Pre-breakout / rising GMV preferred

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| FastMoss payment blocked on main site | Try **developer free trial** (separate billing) or use **Kalodata** |
| Kalodata “insufficient credits” | Top up in Kalodata account or reduce scout frequency |
| Kalodata “membership required” | Upgrade from free trial to Starter |
| Scout parses zero products | Re-run; check `scout_cli ping` output preview |

---

## Do not use

- **EchoTik** — retired for this project
- **$500/mo Enterprise API** on either platform unless you choose to negotiate later

Legacy EchoTik doc: `docs/FOR_OWNER_ECHOTIK_SETUP.md`  
FastMoss detail: `docs/FOR_OWNER_FASTMOSS_SETUP.md`
