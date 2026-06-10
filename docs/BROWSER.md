# Web browser control

Soft Continuity uses **Playwright Chromium** with a saved profile at `data/browser_profile/`.  
Both the **Discord bot** and the **AI strategist** can run browsers.

## Install

```bash
python3 -m playwright install chromium
python3 -m shorts_bot.browser.cli status
```

## Discord / chat commands

| Command | Action |
|---------|--------|
| `browse https://vidiq.com` | Headless — returns page text |
| `browse vidiq` | Same (site alias) |
| `browser open vidiq` | Visible browser on Desktop (15 min) |
| `browser login youtube` | Open login tab — session saved to profile |
| `browser status` | Playwright + profile check |

Discord: `!browse`, `!browser open`, `!browser login`

## CLI

```bash
python3 -m shorts_bot.browser.cli browse trends
python3 -m shorts_bot.browser.cli open vidiq --minutes 20 --block
python3 -m shorts_bot.login_handoff --only vidiq
```

## AI agent tools

When chat has Gemini/OpenAI, the strategist can call:

- `browse_web` — headless research
- `open_browser` — human login on Desktop

## Deep research

When HTTP fetch fails (Cloudflare, JS pages), deep research automatically retries with **headless browser** (`BROWSER_USE_FOR_RESEARCH=true`).

## Config (`.env`)

| Variable | Default | Meaning |
|----------|---------|---------|
| `BROWSER_ENABLED` | true | Master switch |
| `BROWSER_HEADLESS` | true | Automation uses headless |
| `BROWSER_ALLOW_VISIBLE` | true | Allow `browser open` |
| `BROWSER_USE_FOR_RESEARCH` | true | Browser fallback in deep research |
| `BROWSER_OPEN_MINUTES` | 15 | Visible session length |

## Site aliases

`vidiq`, `youtube`, `studio`, `trends`, `turboscribe`, `google`, `capcut`, `discord`
