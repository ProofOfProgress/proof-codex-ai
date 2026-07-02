# Hands-off product scout (owner does nothing ongoing)

You asked to be **pinched off** from the scout pipeline. This is the setup.

---

## Best path: KaloPilot API (no browser, no Edge, no clicking)

| You do **once** | Agent does forever |
|-----------------|-------------------|
| Copy token from [kalodata.com/pilot](https://kalodata.com/pilot) (bottom-left → Connect OpenClaw) | Runs all course methods (middle core, hardcore, lurkers, 100 gap, 200) |
| Add to **Cursor secrets** → start **new agent run** | Saves `products.json` + scout report |
| | Coach filters applied (≥8% commission, ≥$80, ≤200 creators) |

### Secrets (Cursor → new cloud agent)

| Secret | Value |
|--------|--------|
| `KALODATA_PILOT_TOKEN` | Long hex token from kalodata.com/pilot |
| `SCOUT_PROVIDER` | `auto` (default — KaloPilot wins when token is set) |

### Test

```bash
python3 -m shorts_bot.tiktok_shop.scout_cli ping
python3 -m shorts_bot.tiktok_shop.scout_autorun
```

**Credits:** ~10 per query. Your Pro plan includes KaloPilot credits — top up in Kalodata if low.

---

## Fallback: Hub Edge CDP (if you skip pilot token)

Reuses your **existing Edge Kalodata login** — no separate Playwright login.

1. Once per boot (if Edge wasn’t started with debug):

```bash
bash scripts/hub_edge_cdp_start.sh
```

2. Log into Kalodata in that Edge window if needed.

3. Agent attaches via port 9222 and applies filters with DOM (no coordinate clicks).

---

## What NOT to do

- Do not paste filter URLs manually (fallback only)
- Do not watch agent click in Edge (`--legacy-desktop` is banned)
- Do not use Momentum Product Scout tool (banned)

---

## Architecture note (Gemini consult 2026-07-02)

Gemini API was unavailable (503). Engineering decision matches standard advice:

1. **API-first** (KaloPilot) for owner-free launch  
2. **CDP-second** (reuse Edge session)  
3. **Playwright profile-third** (cold Cloudflare — avoid)

Full detail: `data/research/inbox/kalodata-hands-off-architecture-2026-07-02.md`
