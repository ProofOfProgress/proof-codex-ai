# Operating rules seed — minimal

## Strategy source (supreme)

**Owner's paid TikTok Shop course** — when transcribed, that becomes the **only** playbook.

- **Never contradict the course** unless the **owner** (or someone the owner explicitly designates) gives a direct override.
- **Do not** let analytics, self-learning, or archived guru docs override the course.
- Analytics / reward scoring is **optional** and **off by default** for strategy — the course already knows more than we do.

When course modules are pasted → save verbatim to `data/research/course/` → build a structured playbook → **inject that playbook into every factory step** (scout filters, hooks, captions, render style, posting SOP).

## Mandatory pre-upload QC (Module 1)

**REQUIRED before every video upload.** Run Module 1 checklist — **zero** Video Don'ts and Posting Don'ts or upload is blocked.

- Code: `shorts_bot/tiktok_shop/module1_qc.py`
- Enforced in `post_clip()` — no upload without pass
- Course reference: `data/research/course/module_01_read_before_anything.md`
- Never skip unless owner explicitly disables in `.env` (emergency only)

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

## Archived code

`archive/legacy/` — ignore unless owner pivots.
