# AGENTS.md — TikTok Shop only

## Owner (read first)

- **Not a developer** — plain English, exact steps, no code tours.
- **North star:** **TikTok Shop money** — affiliate clips + (optional) seller/Printify later. Target **$5–10K/mo** via winning products, video volume, affiliates, then ads.
- **Top 4 only:** `data/PRIORITIES.md` — nothing else until reassessed.
- **Owner is in a paid affiliate course** — when they paste transcripts, ingest into `data/research/` playbooks (private repo only).

## Project = TikTok Shop Factory

**Stack:** EchoTik scout → Kling 1080p faceless clips → post queue (Zernio / TikTok API) → Printify when seller path.

```bash
bash scripts/install.sh
python3 -m shorts_bot.tiktok_shop status
python3 -m shorts_bot.tiktok_shop.scout_cli run --preset middle_core --limit 10
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "NAME" --style auto
python3 -m shorts_bot.tiktok_shop.printify_cli status   # seller / POD
python3 -m src.clock --json
```

**Web (API status):** `python3 -m shorts_bot.web` → http://127.0.0.1:8080

## Keep / do not restore without owner ask

| Keep | Why |
|------|-----|
| `shorts_bot/tiktok_shop/` | Core factory |
| `shorts_bot/tiktok/` | TikTok OAuth + upload API |
| `shorts_bot/production/images/` + `ai_video_prompts.py` | Video gen / Kling prompts |
| `shorts_bot/config.py` | All API keys (EchoTik, Kling, Printify, TikTok, Slack, etc.) |
| `shorts_bot/integrations/` | Slack webhooks |
| `shorts_bot/zernio/` | Multi-platform post helper |

## Archived (legacy)

**Peripheral horror YouTube, Ms Byte, InVideo, Codex, agents** → `archive/legacy/` — do not wire back unless owner explicitly pivots.

## Secrets

`docs/CURSOR_SECRETS.md` — EchoTik, Kling JWT, Printify, TikTok OAuth, Zernio.

## Tests

```bash
python3 -m pytest tests/ -q
```

## Git / PR

Cloud agents merge own PRs when tests pass. Branch prefix: `cursor/<name>-4484`.
