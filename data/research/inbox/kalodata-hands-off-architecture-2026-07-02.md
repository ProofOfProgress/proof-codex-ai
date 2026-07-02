# Kalodata hands-off architecture — 2026-07-02

## Owner request
Be **pinched off** from product scout — zero ongoing manual work at launch.

## Gemini consultation
Attempted models: `gemini-2.5-flash-lite`, `gemini-2.0-flash`, `gemini-1.5-flash`.
Result: **503 / 404** — unavailable during implementation.

## Decision (matches expected Gemini recommendation)

| Priority | Path | Owner ongoing work |
|----------|------|-------------------|
| **1** | `KALODATA_PILOT_TOKEN` → KaloPilot API | **None** after one secret |
| **2** | Edge CDP `127.0.0.1:9222` → Playwright attach | None after boot script |
| **3** | Playwright profile + visible login | Re-login when session expires |
| ~~4~~ | Desktop x,y clicks | **Removed** — misclicks, closed Edge |

## Implemented
- `kalodata_pilot_queries.py` — course method queries mirror `build_spec()`
- `scout_provider` auto order: **kalodata before hub_ui**
- `scout_autorun.run_kalopilot_multi_scout()` — all P0 methods in one run
- `kalodata_edge_cdp.py` + `scripts/hub_edge_cdp_start.sh`
- Playwright apply tries CDP first, falls back to profile
- `docs/FOR_OWNER_HANDS_OFF_SCOUT.md`

## Single unavoidable owner action
Add **`KALODATA_PILOT_TOKEN`** to Cursor secrets (2 minutes, once).

Alternative: run `hub_edge_cdp_start.sh` once per Windows boot if refusing pilot token.
