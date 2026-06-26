# Higgsfield in Cursor — setup (Module 4 + 5)

Use Higgsfield from Cursor chat for **affiliate product images and video** (course Modules 4 and 5).

This repo includes the official Higgsfield Cursor plugin at `.cursor/plugins/higgsfield/`.

## Quick setup (Desktop)

```bash
bash scripts/higgsfield-setup.sh
```

Then in Cursor:

1. **Reload** — Command Palette → `Developer: Reload Window`
2. **Plugins** — Settings → Plugins → **Higgsfield** should appear
3. **Sign in** — Settings → Tools & MCP → **higgsfield** → Connect (browser OAuth)
4. **Cloud agents** — [Cursor Dashboard → Integrations](https://cursor.com/dashboard?tab=integrations) → enable **Higgsfield MCP**
5. **New agent run** — start a fresh cloud agent after auth (VM only picks up MCP at launch)

## Alternative: Marketplace install

In Cursor chat: `/add-plugin` → search **Higgsfield** → install.

Or: [cursor.com/marketplace/higgsfield](https://cursor.com/marketplace/higgsfield)

The vendored copy in this repo pins a known version; re-run `bash scripts/higgsfield-setup.sh` after `git pull` to refresh Desktop.

## What to ask the agent

**Module 4 — image** (after ChatGPT Prompt Builder output):

```
Generate a 9:16 product image: [paste prompt]. NanoBanana style, 2K, photorealistic.
```

**Module 5 — video** (upload Module 4 image first, or reference a local file):

```
/higgs Animate this product shot — Kling 2.6, 5 seconds, 9:16, audio off.
Use prompt: Arc Camera Shot from left to right, handheld but naturally stabilized...
```

Fixed video prompt (do not change): `data/research/course/module_05_ai_video_generation.md`

## Repo vs bot automation

| Path | What it does |
|------|----------------|
| **Higgsfield in Cursor** | You or the agent generate images/video in chat |
| **`shorts_bot/` factory** | Automated pipeline (Kling API keys, QC, queue) — separate |

Higgsfield MCP does **not** replace `KLING_ACCESS_KEY` in the bot. Use chat for hands-on clips; use the factory when automation is wired.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| MCP shows **needs auth** | Finish OAuth in Desktop; enable for Cloud Agents; **new agent run** |
| Tools missing after pull | Re-run `bash scripts/higgsfield-setup.sh` and reload Cursor |
| Wrong image size | Say **9:16** and **2K** explicitly (Module 4 defaults) |

Support: [higgsfield-ai/cursor-plugin issues](https://github.com/higgsfield-ai/cursor-plugin/issues)
