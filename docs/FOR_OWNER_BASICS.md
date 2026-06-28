# TikTok Shop bot — basics only

**Strategy:** `data/research/course/` only.

## One-time setup

```bash
bash scripts/install.sh
python3 -m shorts_bot.tiktok_shop status
python3 -m shorts_bot.tiktok_shop.printify_cli status   # if using Printify
```

Secrets checklist: `docs/CURSOR_SECRETS.md`  
Mini PC install (phones + hub): `docs/FOR_OWNER_MINI_PC_INSTALL.md`  
**Agent remote control (SSH):** `docs/FOR_OWNER_REMOTE_HUB_SSH.md`  
Launch timeline: `docs/LAUNCH_CHECKLIST.md`  
Launch budget (runway): `docs/LAUNCH_BUDGET.md`  
Launch to-do (in order): `docs/LAUNCH_TODO.md`  
Launch prep status: `docs/LAUNCH_PREP_BRIEF.md`  
Pipeline design: `docs/PIPELINE_SYSTEM_DESIGN.md`  
Cursor rules: **`docs/FOR_OWNER_CURSOR_RULES.md`** (`.cursor/rules/`)  
Higgsfield (Module 4/5 in chat): `docs/FOR_OWNER_HIGGSFIELD_SETUP.md`  
FastMoss (replaces EchoTik): `docs/FOR_OWNER_FASTMOSS_SETUP.md`  
Kling: `docs/FOR_OWNER_KLING_SETUP.md`  
Printify: `docs/FOR_OWNER_PRINTIFY_API.md`  
TikTok posting (easy): `docs/FOR_OWNER_ZERNIO_SETUP.md`  
TikTok direct API (hard mode): `docs/FOR_OWNER_TIKTOK_SETUP.md`

## Make a clip (no strategy — just the button)

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "Product name"
```

## API status

```bash
python3 -m shorts_bot.web
```

Open http://127.0.0.1:8080/api/status
