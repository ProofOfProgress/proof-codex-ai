# Agent autonomy (2026)

How the CEO agent runs **without the owner** for hours/days.

## What runs where

| Job | Where | Tool |
|-----|-------|------|
| Momentum Academy crawl | Hub WSL | Playwright `momentum_academy` profile |
| Discord read-only | Hub WSL | Playwright `discord` profile |
| Kalodata scout | Hub WSL | Playwright + XHR sniff (not KaloPilot credits) |
| Affiliate pipeline | Cloud VM | factory_cli, Kling, QC |
| Phone finish (Mackenzie, cart) | Hub | ADB via **Windows** `adb.exe` (USB to HP) |

## Owner ping

When blocked (login, SMS, CAPTCHA, payment):

```bash
python3 -m shorts_bot.owner_ping "Need Kalodata SMS code on hub"
```

Needs `SLACK_CHANNEL_EMAIL` + Gmail SMTP **or** Slack bot — see `docs/FOR_OWNER_SLACK_EMAIL.md`.

## Self-continue (CEO loop)

Problem: cloud agent stops after one reply.

**Phase 1 (now):** Mission log + owner starts new run or prelaunch scheduler clicks Cursor Run (`docs/FOR_OWNER_DESKTOP_HELPER.md`).

**Phase 2 (now):** `python3 -m shorts_bot.agent_ops mission continue` — reads last mission todo, suggests next step.

**Phase 3:** Cron on hub: daily `hub_course_deep_crawl.sh` + `hub_discord_crawl.sh` → inbox; cloud `hub_pull_intel.sh` on next agent run.

## Intel outputs

| Path | Content |
|------|---------|
| `data/research/course/inbox/momentum-deep-crawl-*.md` | Full course index |
| `data/research/course/inbox/momentum-deep/*.md` | Per-page dumps |
| `data/research/course/inbox/discord-crawl-*.md` | Discord channels |
| `data/tiktok_shop/momentum_weekly_drop.json` | Parsed weekly products |
| `data/tiktok_shop/momentum_scout_rules.yaml` | Scout filter rules from course |

## Phone at hub (USB)

WSL does **not** see USB phones by default. Use:

1. `bash scripts/hub_adb_windows.sh` — Windows adb
2. If empty: Admin PowerShell `scripts/hub_usbipd_attach.ps1` then WSL adb

One phone plugged in = bind to `phone_1` when serial appears.

## Discord one-time login

On hub (owner once, or Playwright headless after creds):

```bash
python3 -m shorts_bot.browser.cli open discord --minutes 10 --block
```

Then `bash scripts/hub_discord_crawl.sh` works unattended.

## Do not

- Open Copilot on hub desktop
- Burn KaloPilot credits on daily scout
- Use vision/Gemini to click Kalodata filters
- Commit passwords or post to Discord/TikTok
