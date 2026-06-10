# vidIQ setup for Soft Continuity

vidIQ feeds **keyword volume, competition, and related queries** into deep research.

## Option A — MCP API key (fastest for automation)

Best if you have **vidIQ Max** (includes MCP).

1. Open [vidIQ MCP](https://vidiq.com/mcp/) → create API key
2. Add to `.env`:
   ```
   VIDIQ_API_KEY=your_key_here
   ```
3. Deep research calls `https://mcp.vidiq.com/mcp` automatically

**Cursor IDE:** You can also add the same MCP server in Cursor settings (`https://mcp.vidiq.com/mcp`) so *this agent* can query vidIQ during chat — separate from the bot pipeline but same account.

## Option B — Browser session (no API key)

1. Desktop login:
   ```bash
   python3 -m shorts_bot.login_handoff --only vidiq
   ```
2. Sign into vidIQ in the opened browser tab (saved to `data/browser_profile/`)
3. Deep research scrapes `app.vidiq.com/research` keyword tab

Check: `python3 -m shorts_bot.login_status` → vidIQ row

## Option C — CSV export (manual fallback)

1. In vidIQ web app: **Search → Keywords** → export CSV
2. Drop file in `data/vidiq_exports/` (create folder if needed)
3. Next research run picks up the latest export

## Free plan note

Free vidIQ shows limited keyword rows (3–4 per search). Paid plans unlock full lists — still useful for deep research direction.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Not logged in" | `login_handoff --only vidiq` |
| MCP 401 | Regenerate API key; confirm Max plan |
| Empty keywords | Export CSV to `data/vidiq_exports/` |
| Skip vidIQ entirely | `VIDIQ_ENABLED=false` in `.env` |
