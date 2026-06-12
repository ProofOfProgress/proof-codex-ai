# Deep research

When you say **deep research** or `research <topic>`, the bot does **not** only read local files. It runs a full stack:

1. **Web browsing** — DuckDuckGo search (+ optional Tavily if `TAVILY_API_KEY` set), fetches page snippets
2. **YouTube autocomplete** — real search suggestions for Shorts angles
3. **YouTube Data API** — competitor Short titles on your topic
4. **Google Trends** — YouTube-search related + rising queries (`pytrends`)
5. **Browser** (optional) — headless fetch when pages block HTTP (`browse trends`)
6. **Jenny Hoyos course** — hook, framing, retention rules in the synthesis prompt
7. **LLM synthesis** — merges everything into cached `data/research/<topic>.json`
8. **Credible sources** — Tier A/B required for scare/audio/psychology claims (peer-reviewed, academic film-sound, expert institutions); Tier C for CapCut workflow only. See `data/research/HORROR_SOUND_EFFECTS_RESEARCH.md` §1.

vidIQ is **off by default** (paid). Use Trends + browser instead.

Output includes **recommended_path** — the smoothest, fastest way to run the pipeline (`daily_cli`, captions, upload).

## Commands

```bash
python3 -m shorts_bot.production.research_cli "the minute before a hard conversation"
python3 -m shorts_bot.production.research_cli --refresh   # re-browse web
```

Web chat:

- `research <topic>` — cached if fresh
- `deep research <topic>` — force refresh
- `daily <topic>` — research is step 1 of autopilot

## What gets used downstream

- **Draft generation** — `research.draft_context()` in Gemini prompt
- **Upload metadata** — `title_formula` + keyword tags from research
- **`!draft`** — now runs deep research before scripting

## Disable web

`.env`: `RESEARCH_WEB_ENABLED=false` (course + LLM only)

## Optional boosters

| Variable | Effect |
|----------|--------|
| `TAVILY_API_KEY` | Higher-quality web summaries |
| `GOOGLE_TRENDS_ENABLED=false` | Skip Trends step |
| `GOOGLE_TRENDS_GPROP=youtube` | Trends property (`youtube` = YouTube search) |
| `GOOGLE_TRENDS_GEO=US` | Region filter |
| `VIDIQ_ENABLED=true` | Re-enable paid vidIQ (not recommended) |

See `docs/BROWSER.md` for keyword research via browser.
