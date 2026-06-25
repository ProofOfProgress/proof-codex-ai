# AGENTS.md — TikTok Shop

## Owner

- Not a developer — plain English, exact steps.
- **Business playbook = owner's paid course** (when transcribed). Do **not** use archived guru docs or old seller/affiliate writeups in this repo.
- **Top 4:** `data/PRIORITIES.md` (technical until course is ingested).

## What the bot does (technical only)

Connect APIs → scout products → Kling clips → queue/post.

```bash
bash scripts/install.sh
python3 -m shorts_bot.tiktok_shop status
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "NAME"
python3 -m shorts_bot.web   # http://127.0.0.1:8080/api/status
```

## Keep connected (do not break)

| Area | Path |
|------|------|
| Shop factory | `shorts_bot/tiktok_shop/` |
| TikTok OAuth/upload | `shorts_bot/tiktok/` |
| API keys | `shorts_bot/config.py`, `docs/CURSOR_SECRETS.md` |
| Video gen helpers | `shorts_bot/production/images/`, `ai_video_prompts.py` |
| Posting helpers | `shorts_bot/zernio/`, `shorts_bot/integrations/` |
| Browser login handoff | `shorts_bot/browser/` |
| Self-learning loop | `shorts_bot/rewards/`, `shorts_bot/learning/`, `shorts_bot/training/`, `shorts_bot/memory/` — optional; course is strategy source |
| **Module 1 QC (mandatory)** | `shorts_bot/tiktok_shop/module1_qc.py` — **blocks upload** if any ban trigger; run before every post |

## Course ingest

Owner pastes transcripts → `data/research/course/` → agent builds playbook on request.

## Tests

```bash
python3 -m pytest tests/ -q
```

## Legacy

`archive/legacy/` — do not restore without owner ask.
