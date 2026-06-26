# Operating rules seed — minimal

## Strategy source (supreme)

**Owner's paid TikTok Shop affiliate course** — `data/research/course/` is the **only** creative playbook.

- **~90% of agent knowledge** for content (hooks, visuals, captions, growth, compliance) must come from the course modules.
- **Repo code** is for automation only (APIs, render, QC gate, queue) — not for inventing strategy.
- **Never contradict the course** unless the **owner** gives a direct override.
- No other strategy docs, guru content, or old courses in this repo.
- Hierarchy: `data/research/course/KNOWLEDGE.md`

## Retired (dead — do not reference)

Fix It Fast · Rapid Tool Review · Ms. Byte · InVideo daily workflow · Peripheral horror · any deleted `archive/` strategy not re-ingested into `course/`.

## Mandatory pre-upload QC (Module 1)

**REQUIRED before every video upload.** Zero Video Don'ts and Posting Don'ts or upload is blocked.

- Code: `shorts_bot/tiktok_shop/module1_qc.py`
- Course: `data/research/course/module_01_read_before_anything.md`

## Prompt builder (owner override)

**Do not use** the course Google Sheet auto-prompter.

**Use** ChatGPT Product Video Prompt Builder — see `data/research/course/PROMPT_BUILDER.md`.

## Owner

Not a developer. Plain English. One step at a time.

## Technical stack (connections only)

- **EchoTik** — product scout API  
- **Kling** — clip render API  
- **Printify** — POD listings API (optional)  
- **TikTok OAuth** — posting API  
- **Zernio** — multi-platform upload (optional)  
- **Slack** — alerts (optional)  

Secrets: `docs/CURSOR_SECRETS.md`. Run `bash scripts/install.sh` to sync.

## Agents

Use browser + terminal for dashboards. Ask owner only for 2FA, payment, wrong account.
