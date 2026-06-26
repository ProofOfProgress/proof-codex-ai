# AGENTS.md — TikTok Shop

## Owner

- Not a developer — plain English, exact steps.
- **Only knowledge source:** `data/research/course/` (owner's paid affiliate course).
- **Top 4:** `data/PRIORITIES.md`

## Commands

```bash
bash scripts/install.sh
python3 -m shorts_bot.tiktok_shop status
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "NAME"
python3 -m shorts_bot.web   # http://127.0.0.1:8080/api/status
python3 -m pytest tests/ -q
```

## Code map

| Area | Path |
|------|------|
| Shop factory | `shorts_bot/tiktok_shop/` |
| TikTok OAuth | `shorts_bot/tiktok/` |
| API keys | `shorts_bot/config.py`, `docs/CURSOR_SECRETS.md` |
| Module 1 QC (mandatory) | `shorts_bot/tiktok_shop/module1_qc.py` |

## Course

Modules in `data/research/course/`. Prompts: **ChatGPT Product Video Prompt Builder** (`PROMPT_BUILDER.md`) — not the course Google Sheet.
