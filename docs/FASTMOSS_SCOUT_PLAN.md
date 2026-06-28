# FastMoss scout migration plan

**Decision:** FastMoss **replaces** EchoTik. EchoTik code stays in repo as legacy until removed.

---

## Why

- Course creator: FastMoss ≈ Kalodata (full Module 3 checks — ads, trend, filters)
- One subscription instead of EchoTik + manual Kalodata
- FastMoss OpenAPI: product trends, video/ad data, rankings

---

## Phases

### Phase 0 — Launch without bot scout *(now)*

- Owner: FastMoss UI → pick 8–10 products  
- Owner: paste names to CEO → `make-clip` per product  
- **No EchoTik payment**

### Phase 1 — API client *(stub in repo)*

- `shorts_bot/tiktok_shop/fastmoss_client.py` — token auth, ping  
- Secrets: `FASTMOSS_CLIENT_ID`, `FASTMOSS_CLIENT_SECRET`  
- `scout_cli status` / `ping` prefer FastMoss when configured  

### Phase 2 — Scout rewrite

- `product_scout.py` → fetch rankings + trends from FastMoss  
- Map course presets: middle_core, two_hundred, lurkers, 100_gap  
- Score: commission, creators, GMV, **trend direction**, **ad signal** (when API exposes)  
- Save to `products.json` same schema  

### Phase 3 — Retire EchoTik

- Remove `echotik_client` from scout path  
- Mark `FOR_OWNER_ECHOTIK_SETUP.md` deprecated  
- Drop `ECHOTIK_*` from required secrets  

---

## Owner action to unblock Phase 1–2

1. FastMoss subscription (UI)  
2. Developer account → `client_id` + `client_secret`  
3. Add secrets → new agent run  
4. Tell agent: “Wire FastMoss scout”

---

## Reference

- GitHub: https://github.com/FastMoss/openapi  
- Developer portal: https://developers.fastmoss.com/
