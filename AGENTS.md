# AGENTS.md — TikTok Shop

## Owner

- Not a developer — plain English, exact steps.
- **Top 4:** `data/PRIORITIES.md`

## Knowledge (read this first)

| Layer | Source | What it covers |
|-------|--------|----------------|
| **Creative (~90%)** | `data/research/course/` | Hooks, images, video, editing, growth, violations, appeals |
| **Automation (~10%)** | `shorts_bot/tiktok_shop/`, APIs | EchoTik, Kling, OAuth, Module 1 QC gate, posting mechanics |

Full hierarchy: `data/research/course/KNOWLEDGE.md`

**Dead brands — never use for creative direction:** Fix It Fast, Rapid Tool Review, Ms. Byte, InVideo, Peripheral horror.

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
