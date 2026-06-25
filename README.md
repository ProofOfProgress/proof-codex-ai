# TikTok Shop Factory

**100% focus:** TikTok Shop affiliate/seller clips — scout products, Kling-render faceless video, queue posts.

Legacy Peripheral / YouTube / horror code lives in **`archive/legacy/`** (not maintained).

## Quick start

```bash
bash scripts/install.sh
python3 -m shorts_bot.tiktok_shop status
python3 -m shorts_bot.tiktok_shop.factory_cli rules
python3 -m shorts_bot.web   # http://127.0.0.1:8080/api/status
python3 -m pytest tests/ -q
```

## CLI

| Command | Purpose |
|---------|---------|
| `python3 -m shorts_bot.tiktok_shop.scout_cli run` | EchoTik product scout |
| `python3 -m shorts_bot.tiktok_shop.factory_cli make-clip` | Render + loop + enqueue |
| `python3 -m shorts_bot.tiktok_shop.printify_cli sync` | Your Printify listings |
| `python3 -m shorts_bot.tiktok auth_cli` | TikTok OAuth (posting API) |

## Docs

See `docs/FOR_OWNER_TIKTOK_*.md` and `data/PRIORITIES.md`.
