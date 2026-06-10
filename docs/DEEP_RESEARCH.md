# Deep research

When you say **deep research** or `research <topic>`, the bot does **not** only read local files. It runs a full stack:

1. **Web browsing** — DuckDuckGo search (+ optional Tavily if `TAVILY_API_KEY` set), fetches page snippets
2. **YouTube autocomplete** — real search suggestions for Shorts angles
3. **YouTube Data API** — competitor Short titles on your topic
4. **Google Trends** — YouTube-search related + rising queries (`pytrends`, geo/property configurable)
5. **vidIQ** — keyword volume/competition (MCP API key, browser session, or CSV export)
6. **Jenny Hoyos course** — hook, framing, retention rules in the synthesis prompt
7. **LLM synthesis** — merges everything into cached `data/research/<topic>.json`

Output includes **recommended_path** — the smoothest, fastest way to run the pipeline (`daily_cli`, captions, upload).

## Commands

```bash
python3 -m shorts_bot.production.research_cli "the minute before a hard conversation"
python3 -m shorts_bot.production.research_cli --refresh   # re-browse web
```

Discord / chat:

- `research <topic>` — cached if fresh
- `deep research <topic>` / `!deepresearch <topic>` — force refresh
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
| `VIDIQ_API_KEY` | vidIQ Max MCP at mcp.vidiq.com |
| `VIDIQ_ENABLED=false` | Skip vidIQ step |
| `VIDIQ_USE_BROWSER=false` | API/CSV only, no Playwright |

See `docs/VIDIQ_SETUP.md`.
