# TikTok Shop bot — basics only

**Strategy comes from your paid course**, not this file.

## One-time setup

```bash
bash scripts/install.sh
python3 -m shorts_bot.tiktok_shop status
python3 -m shorts_bot.tiktok_shop.printify_cli status   # if using Printify
```

Secrets checklist: `docs/CURSOR_SECRETS.md`  
EchoTik: `docs/FOR_OWNER_ECHOTIK_SETUP.md`  
Kling: `docs/FOR_OWNER_KLING_SETUP.md`  
Printify: `docs/FOR_OWNER_PRINTIFY_API.md`  
TikTok login: `docs/FOR_OWNER_TIKTOK_SETUP.md`

## Make a clip (no strategy — just the button)

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "Product name"
```

## API status

```bash
python3 -m shorts_bot.web
```

Open http://127.0.0.1:8080/api/status

## Course transcripts

Paste modules into `data/research/course/` and tell the agent **ingest the course**.
